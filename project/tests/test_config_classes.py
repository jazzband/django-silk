from unittest.mock import patch

from django.test import TestCase

from silk.config import SilkyConfig
from silk.model_factory import RequestModelFactory, ResponseModelFactory


class DummyRequestModelFactory(RequestModelFactory):
    pass


class DummyResponseModelFactory(ResponseModelFactory):
    pass


class TestRequestModelFactoryClass(TestCase):

    def test_config_with_no_value_should_have_default(self):
        config = SilkyConfig()
        self.assertEqual(config.SILKY_REQUEST_MODEL_FACTORY_CLASS, 'silk.model_factory.RequestModelFactory')

    def test_config_with_no_value_should_have_request_model_factory_property(self):
        config = SilkyConfig()
        self.assertTrue(hasattr(config, 'request_model_factory'))

    @patch.dict(SilkyConfig().attrs, {
        'SILKY_REQUEST_MODEL_FACTORY_CLASS': 'tests.test_config_classes.DummyRequestModelFactory'
    })
    def test_config_with_custom_class_should_load_custom_class(self):
        config = SilkyConfig()
        self.assertIs(config.request_model_factory, DummyRequestModelFactory)


class TestResponseModelFactoryClass(TestCase):

    def test_config_with_no_value_should_have_default(self):
        config = SilkyConfig()
        self.assertEqual(config.SILKY_RESPONSE_MODEL_FACTORY_CLASS, 'silk.model_factory.ResponseModelFactory')

    def test_config_with_no_value_should_have_response_model_factory_property(self):
        config = SilkyConfig()
        self.assertTrue(hasattr(config, 'response_model_factory'))

    @patch.dict(SilkyConfig().attrs, {
        'SILKY_RESPONSE_MODEL_FACTORY_CLASS': 'tests.test_config_classes.DummyResponseModelFactory'
    })
    def test_config_with_custom_class_should_load_custom_class(self):
        config = SilkyConfig()
        self.assertIs(config.response_model_factory, DummyResponseModelFactory)

