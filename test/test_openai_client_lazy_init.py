#!/usr/bin/env python3
"""
Test script for the OpenAI client lazy initialization fix.

This test verifies that the OpenAI client can be instantiated without
requiring OPENAI_API_KEY environment variable, but still fails
appropriately when actually used without the API key.

Addresses issue: https://github.com/takpanda/deepwiki-open/issues/1
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the module under test
from api.openai_client import OpenAIClient

class TestOpenAIClientLazyInit:
    """Test lazy initialization of OpenAI client to fix Ollama usage issue"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        # Store original environment
        self.original_api_key = os.environ.get('OPENAI_API_KEY')
        
    def teardown_method(self):
        """Clean up test environment after each test"""
        # Restore original environment
        if self.original_api_key:
            os.environ['OPENAI_API_KEY'] = self.original_api_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_openai_client_instantiation_without_api_key(self):
        """Test that OpenAI client can be instantiated without API key"""
        # Remove API key from environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # This should work now with lazy initialization
        client = OpenAIClient()
        
        # Verify lazy initialization properties
        assert client.sync_client is None, "sync_client should be None until needed"
        assert client.async_client is None, "async_client should be None until needed"
        assert hasattr(client, 'get_sync_client'), "Should have get_sync_client method"
        assert hasattr(client, 'get_async_client'), "Should have get_async_client method"
        
        print("✓ OpenAI client instantiated successfully without API key")
    
    def test_openai_client_fails_when_used_without_api_key(self):
        """Test that OpenAI client fails appropriately when used without API key"""
        # Remove API key from environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        client = OpenAIClient()
        
        # Trying to get sync client should fail
        with pytest.raises(ValueError) as exc_info:
            client.get_sync_client()
        
        assert "Environment variable OPENAI_API_KEY must be set" in str(exc_info.value)
        print("✓ OpenAI client correctly fails when used without API key")
    
    def test_openai_client_works_with_api_key(self):
        """Test that OpenAI client works normally when API key is provided"""
        # Set a test API key
        os.environ['OPENAI_API_KEY'] = 'test-api-key-123'
        
        client = OpenAIClient()
        
        # Mock the OpenAI library to avoid actual API calls
        with patch('api.openai_client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            
            # This should work without errors
            sync_client = client.get_sync_client()
            
            # Verify OpenAI constructor was called with correct parameters
            mock_openai.assert_called_once_with(
                api_key='test-api-key-123',
                base_url='https://api.openai.com/v1'
            )
            
            print("✓ OpenAI client works correctly with API key")
    
    def test_openai_client_explicit_api_key(self):
        """Test that OpenAI client works with explicitly provided API key"""
        # Remove environment API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Create client with explicit API key
        client = OpenAIClient(api_key='explicit-test-key')
        
        with patch('api.openai_client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            
            sync_client = client.get_sync_client()
            
            # Verify explicit API key was used
            mock_openai.assert_called_once_with(
                api_key='explicit-test-key',
                base_url='https://api.openai.com/v1'
            )
            
            print("✓ OpenAI client works with explicit API key")
    
    def test_openai_client_lazy_async_initialization(self):
        """Test that async client is also lazily initialized"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        client = OpenAIClient()
        
        # async_client should be None initially
        assert client.async_client is None
        
        # Trying to get async client should fail without API key
        with pytest.raises(ValueError) as exc_info:
            client.get_async_client()
        
        assert "Environment variable OPENAI_API_KEY must be set" in str(exc_info.value)
        print("✓ Async client also uses lazy initialization correctly")
    
    def test_openai_client_multiple_instantiations(self):
        """Test that multiple client instances can be created without interference"""
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Create multiple clients
        client1 = OpenAIClient()
        client2 = OpenAIClient(api_key='test-key-2')
        client3 = OpenAIClient()
        
        # All should be created successfully
        assert client1.sync_client is None
        assert client2.sync_client is None
        assert client3.sync_client is None
        
        # Test that they behave independently
        with patch('api.openai_client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            
            # Only client2 should work (has explicit API key)
            client2.get_sync_client()
            mock_openai.assert_called_with(api_key='test-key-2', base_url='https://api.openai.com/v1')
            
        # client1 and client3 should still fail
        with pytest.raises(ValueError):
            client1.get_sync_client()
        with pytest.raises(ValueError):
            client3.get_sync_client()
            
        print("✓ Multiple client instances work independently")


def run_tests():
    """Run all tests manually if called as script"""
    test_instance = TestOpenAIClientLazyInit()
    
    print("Running OpenAI Client Lazy Initialization Tests")
    print("=" * 55)
    
    tests = [
        test_instance.test_openai_client_instantiation_without_api_key,
        test_instance.test_openai_client_fails_when_used_without_api_key,
        test_instance.test_openai_client_works_with_api_key,
        test_instance.test_openai_client_explicit_api_key,
        test_instance.test_openai_client_lazy_async_initialization,
        test_instance.test_openai_client_multiple_instantiations,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test_instance.setup_method()
            test()
            test_instance.teardown_method()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
            test_instance.teardown_method()
    
    print("\n" + "=" * 55)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The OpenAI client lazy initialization fix works correctly.")
        return True
    else:
        print("❌ Some tests failed. The fix may need more work.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)