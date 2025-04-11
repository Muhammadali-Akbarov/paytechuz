"""
Tests for the gateway module.
"""
import unittest
from unittest.mock import patch, MagicMock

from paytechuz import create_gateway


class TestCreateGateway(unittest.TestCase):
    """
    Test the create_gateway function.
    """
    
    def test_create_payme_gateway(self):
        """
        Test creating a Payme gateway.
        """
        with patch('paytechuz.gateway.PaymeGateway') as mock_payme:
            mock_instance = MagicMock()
            mock_payme.return_value = mock_instance
            
            gateway = create_gateway(
                'payme',
                payme_id='test-id',
                payme_key='test-key',
                is_test_mode=True
            )
            
            self.assertEqual(gateway, mock_instance)
            mock_payme.assert_called_once_with(
                payme_id='test-id',
                payme_key='test-key',
                is_test_mode=True
            )
    
    def test_create_click_gateway(self):
        """
        Test creating a Click gateway.
        """
        with patch('paytechuz.gateway.ClickGateway') as mock_click:
            mock_instance = MagicMock()
            mock_click.return_value = mock_instance
            
            gateway = create_gateway(
                'click',
                service_id='test-service-id',
                merchant_id='test-merchant-id',
                secret_key='test-secret-key',
                is_test_mode=True
            )
            
            self.assertEqual(gateway, mock_instance)
            mock_click.assert_called_once_with(
                service_id='test-service-id',
                merchant_id='test-merchant-id',
                secret_key='test-secret-key',
                is_test_mode=True
            )
    
    def test_invalid_gateway_type(self):
        """
        Test creating a gateway with an invalid type.
        """
        with self.assertRaises(ValueError):
            create_gateway('invalid')


if __name__ == '__main__':
    unittest.main()
