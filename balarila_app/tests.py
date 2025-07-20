from django.test import TestCase

# Create your tests here.
# corrector/tests.py

from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase
from balarila_app.schema import schema
from unittest.mock import patch, MagicMock
import json

# --- Test for Core Utility Functions ---
class CorrectorUtilsTest(TestCase):
    """
    Tests for the utility functions that interact with the Balarila model.
    We mock the actual AI model to make tests fast and independent of AI model loading.
    """
    @patch('corrector.utils.get_gec_model')
    def test_check_grammar_function(self, mock_get_model):
        from .utils import check_grammar
        # Configure the mocked AI model's behavior
        mock_model_instance = MagicMock()
        # Mock refactored_handle_batch to return a predictable output
        mock_model_instance.refactored_handle_batch.return_value = (
            [['Corrected', 'text']], 1, [['R:Original->Corrected']]
        )
        mock_get_model.return_value = mock_model_instance

        input_text = "Original text."
        result = check_grammar(input_text)

        # Assertions
        self.assertEqual(result['original_text'], input_text)
        self.assertEqual(result['corrected_text'], "Corrected text")
        self.assertEqual(result['tags'], ['R:Original->Corrected'])
        self.assertEqual(result['corrections_count'], 1)
        mock_get_model.assert_called_once() # Ensure model was accessed
        mock_model_instance.refactored_handle_batch.assert_called_once_with([['Original', 'text.']])

    @patch('corrector.utils.get_gec_model')
    def test_correct_grammar_function(self, mock_get_model):
        from .utils import correct_grammar
        mock_model_instance = MagicMock()
        mock_model_instance.refactored_handle_batch.return_value = (
            [['Fixed', 'sentence']], 1, []
        )
        mock_get_model.return_value = mock_model_instance

        input_text = "Wrong sentence"
        corrected_text = correct_grammar(input_text)

        self.assertEqual(corrected_text, "Fixed sentence")
        mock_get_model.assert_called_once()
        mock_model_instance.refactored_handle_batch.assert_called_once_with([['Wrong', 'sentence']])


# --- GraphQL API Tests ---
class CorrectorGraphQLTest(GraphQLTestCase):
    # This is the schema the test client will use.
    # Make sure to import your main schema here!
    GRAPHQL_SCHEMA = schema

    # Synchronous Query Test
    @patch('corrector.utils.check_grammar')
    def test_check_grammar_query(self, mock_check_grammar):
        # Configure the mocked behavior of the underlying check_grammar function
        mock_check_grammar.return_value = {
            "original_text": "Wrong input.",
            "corrected_text": "Correct input.",
            "tags": ["R:Wrong->Correct"],
            "corrections_count": 1
        }

        query = """
            query {
                checkGrammar(text: "Wrong input.") {
                    originalText
                    correctedText
                    tags
                    correctionsCount
                }
            }
        """
        response = self.query(query)

        self.assertResponseNoErrors(response) # Check for GraphQL errors
        content = json.loads(response.content)

        self.assertEqual(content['data']['checkGrammar']['originalText'], "Wrong input.")
        self.assertEqual(content['data']['checkGrammar']['correctedText'], "Correct input.")
        self.assertEqual(content['data']['checkGrammar']['tags'], ["R:Wrong->Correct"])
        self.assertEqual(content['data']['checkGrammar']['correctionsCount'], 1)
        mock_check_grammar.assert_called_once_with("Wrong input.")