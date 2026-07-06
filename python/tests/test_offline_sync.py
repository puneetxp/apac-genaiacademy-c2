"""
Property-based tests for offline data synchronization
Tests Property 16: Offline Data Synchronization

**Validates: Requirements (Non-Functional - Offline Functionality)**
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


# Simulated offline queue storage (mimics localStorage)
class OfflineQueueStorage:
    """Simulates browser localStorage for offline queue"""
    
    def __init__(self):
        self.storage: Dict[str, str] = {}
    
    def set_item(self, key: str, value: str) -> None:
        """Store item in storage"""
        self.storage[key] = value
    
    def get_item(self, key: str) -> Optional[str]:
        """Retrieve item from storage"""
        return self.storage.get(key)
    
    def remove_item(self, key: str) -> None:
        """Remove item from storage"""
        if key in self.storage:
            del self.storage[key]
    
    def clear(self) -> None:
        """Clear all storage"""
        self.storage.clear()


# Offline queue manager (Python implementation of TypeScript offlineQueue.ts)
class OfflineQueueManager:
    """Manages queuing and syncing of actions performed while offline"""
    
    QUEUE_KEY = 'offline-queue'
    MAX_RETRIES = 3
    
    def __init__(self, storage: OfflineQueueStorage):
        self.storage = storage
        self.is_online = True
    
    def queue_action(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Add an action to the offline queue"""
        queue = self._get_queue()
        
        action = {
            'id': self._generate_id(),
            'type': 'api-request',
            'method': method,
            'url': url,
            'body': body,
            'headers': headers or {},
            'timestamp': int(time.time() * 1000),  # milliseconds
            'retries': 0
        }
        
        queue.append(action)
        self._save_queue(queue)
        
        return action['id']
    
    def _get_queue(self) -> List[Dict[str, Any]]:
        """Get all queued actions"""
        queue_str = self.storage.get_item(self.QUEUE_KEY)
        if not queue_str:
            return []
        try:
            return json.loads(queue_str)
        except json.JSONDecodeError:
            return []
    
    def _save_queue(self, queue: List[Dict[str, Any]]) -> None:
        """Save queue to storage"""
        self.storage.set_item(self.QUEUE_KEY, json.dumps(queue))
    
    def process_queue(self, api_client: Any) -> Dict[str, Any]:
        """
        Process all queued actions
        
        Returns:
            Dict with processed, failed, and remaining counts
        """
        if not self.is_online:
            return {
                'processed': 0,
                'failed': 0,
                'remaining': len(self._get_queue()),
                'status': 'offline'
            }
        
        queue = self._get_queue()
        
        if not queue:
            return {
                'processed': 0,
                'failed': 0,
                'remaining': 0,
                'status': 'empty'
            }
        
        remaining_queue = []
        processed_count = 0
        failed_count = 0
        
        for action in queue:
            try:
                self._process_action(action, api_client)
                processed_count += 1
            except Exception as e:
                action['retries'] += 1
                
                if action['retries'] < self.MAX_RETRIES:
                    remaining_queue.append(action)
                else:
                    failed_count += 1
        
        self._save_queue(remaining_queue)
        
        return {
            'processed': processed_count,
            'failed': failed_count,
            'remaining': len(remaining_queue),
            'status': 'completed'
        }
    
    def _process_action(self, action: Dict[str, Any], api_client: Any) -> Any:
        """Process a single queued action"""
        if action['type'] != 'api-request':
            raise ValueError(f"Unknown action type: {action['type']}")
        
        # Call the API client to execute the request
        return api_client.request(
            method=action['method'],
            url=action['url'],
            body=action.get('body'),
            headers=action.get('headers', {})
        )
    
    def clear_queue(self) -> None:
        """Clear all queued actions"""
        self.storage.remove_item(self.QUEUE_KEY)
    
    def get_queue_size(self) -> int:
        """Get queue size"""
        return len(self._get_queue())
    
    def _generate_id(self) -> str:
        """Generate a unique ID for queued actions"""
        import random
        import string
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"{timestamp}-{random_str}"
    
    def set_online_status(self, is_online: bool) -> None:
        """Set online/offline status"""
        self.is_online = is_online


# Mock API client for testing
class MockAPIClient:
    """Mock API client that simulates server responses"""
    
    def __init__(self):
        self.requests_made: List[Dict[str, Any]] = []
        self.should_fail = False
        self.server_data: Dict[str, Any] = {}
        self.conflict_resolution = 'last-write-wins'
    
    def request(
        self,
        method: str,
        url: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Simulate API request"""
        request_record = {
            'method': method,
            'url': url,
            'body': body,
            'headers': headers,
            'timestamp': time.time()
        }
        self.requests_made.append(request_record)
        
        if self.should_fail:
            raise Exception("API request failed")
        
        # Simulate last-write-wins conflict resolution
        if method in ['POST', 'PUT', 'PATCH'] and body:
            # Extract resource ID from body or URL
            if 'id' in body:
                resource_id = str(body['id'])
            else:
                # Extract from URL (e.g., /farms/123 -> 123)
                url_parts = url.rstrip('/').split('/')
                resource_id = url_parts[-1] if url_parts else 'unknown'
            
            # Check for conflict
            if resource_id in self.server_data:
                # Last write wins - overwrite with new data
                self.server_data[resource_id] = {
                    **body,
                    'updated_at': time.time()
                }
            else:
                # New resource
                self.server_data[resource_id] = {
                    **body,
                    'created_at': time.time()
                }
        
        return {
            'status': 'success',
            'data': body,
            'timestamp': time.time()
        }
    
    def get_requests_count(self) -> int:
        """Get number of requests made"""
        return len(self.requests_made)
    
    def reset(self) -> None:
        """Reset mock client state"""
        self.requests_made.clear()
        self.server_data.clear()
        self.should_fail = False


# Custom strategies for offline action generation
@st.composite
def offline_action_strategy(draw):
    """Generate valid offline actions"""
    
    action_types = [
        {
            'method': 'POST',
            'url': '/farms',
            'body': {
                'name': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
                'state': draw(st.sampled_from(['Punjab', 'Haryana', 'Maharashtra', 'Karnataka', 'Tamil Nadu'])),
                'district': draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L',)))),
                'total_area': draw(st.floats(min_value=0.5, max_value=100.0)),
                'soil_type': draw(st.sampled_from(['clay', 'sandy', 'loamy', 'silt']))
            }
        },
        {
            'method': 'PUT',
            'url': f'/farms/{draw(st.integers(min_value=1, max_value=1000))}',
            'body': {
                'id': draw(st.integers(min_value=1, max_value=1000)),
                'name': draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))),
                'notes': draw(st.text(min_size=0, max_size=200))
            }
        },
        {
            'method': 'POST',
            'url': '/crops',
            'body': {
                'crop_type': draw(st.sampled_from(['wheat', 'rice', 'cotton', 'sugarcane', 'maize'])),
                'variety': draw(st.text(min_size=2, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N')))),
                'planting_date': draw(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date())).isoformat(),
                'area': draw(st.floats(min_value=0.1, max_value=50.0))
            }
        },
        {
            'method': 'POST',
            'url': '/marketplace/listings',
            'body': {
                'crop_type': draw(st.sampled_from(['wheat', 'rice', 'cotton', 'sugarcane', 'maize'])),
                'quantity': draw(st.integers(min_value=10, max_value=10000)),
                'expected_harvest_date': draw(st.dates(min_value=datetime(2024, 1, 1).date(), max_value=datetime(2025, 12, 31).date())).isoformat(),
                'quality_grade': draw(st.sampled_from(['A', 'B', 'C']))
            }
        }
    ]
    
    action = draw(st.sampled_from(action_types))
    
    # Add optional headers
    headers = {}
    if draw(st.booleans()):
        headers['Authorization'] = f"Bearer {draw(st.text(min_size=20, max_size=40, alphabet=st.characters(whitelist_categories=('L', 'N'))))}"
    
    return {
        'method': action['method'],
        'url': action['url'],
        'body': action['body'],
        'headers': headers
    }


@st.composite
def offline_action_sequence_strategy(draw):
    """Generate a sequence of offline actions"""
    num_actions = draw(st.integers(min_value=1, max_value=20))
    actions = [draw(offline_action_strategy()) for _ in range(num_actions)]
    return actions


@st.composite
def conflict_scenario_strategy(draw):
    """Generate conflict scenarios with same resource modified offline and online"""
    resource_id = draw(st.integers(min_value=1, max_value=100))
    
    # Offline modification
    offline_action = {
        'method': 'PUT',
        'url': f'/farms/{resource_id}',
        'body': {
            'id': resource_id,
            'name': draw(st.text(min_size=5, max_size=30, alphabet=st.characters(whitelist_categories=('L',)))),
            'notes': 'Modified offline',
            'timestamp': int(time.time() * 1000)
        }
    }
    
    # Online modification (happens while offline)
    online_action = {
        'method': 'PUT',
        'url': f'/farms/{resource_id}',
        'body': {
            'id': resource_id,
            'name': draw(st.text(min_size=5, max_size=30, alphabet=st.characters(whitelist_categories=('L',)))),
            'notes': 'Modified online',
            'timestamp': int(time.time() * 1000) + 1000  # 1 second later
        }
    }
    
    return {
        'resource_id': resource_id,
        'offline_action': offline_action,
        'online_action': online_action
    }


class TestOfflineDataSynchronization:
    """
    Property 16: Offline Data Synchronization
    
    Test that for any user action performed offline, system queues action locally
    and syncs when connectivity restored, resolving conflicts using last-write-wins strategy.
    """
    
    @given(action=offline_action_strategy())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_offline_action_queued_locally(self, action):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Property: For any user action performed offline, the system should
        queue the action locally in storage.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        queue_manager.set_online_status(False)  # Simulate offline
        
        # Act: Queue an action while offline
        action_id = queue_manager.queue_action(
            method=action['method'],
            url=action['url'],
            body=action['body'],
            headers=action['headers']
        )
        
        # Assert: Action is queued locally
        assert action_id is not None, "Action ID should be generated"
        assert queue_manager.get_queue_size() == 1, "Queue should contain 1 action"
        
        # Assert: Queued action contains all required fields
        queued_actions = queue_manager._get_queue()
        assert len(queued_actions) == 1
        
        queued_action = queued_actions[0]
        assert queued_action['id'] == action_id
        assert queued_action['method'] == action['method']
        assert queued_action['url'] == action['url']
        assert queued_action['body'] == action['body']
        assert queued_action['type'] == 'api-request'
        assert queued_action['retries'] == 0
        assert 'timestamp' in queued_action
    
    @given(actions=offline_action_sequence_strategy())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_multiple_offline_actions_queued_in_order(self, actions):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Property: For any sequence of user actions performed offline, the system
        should queue all actions locally in the order they were performed.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        queue_manager.set_online_status(False)  # Simulate offline
        
        # Act: Queue multiple actions while offline
        action_ids = []
        for action in actions:
            action_id = queue_manager.queue_action(
                method=action['method'],
                url=action['url'],
                body=action['body'],
                headers=action['headers']
            )
            action_ids.append(action_id)
            time.sleep(0.001)  # Small delay to ensure timestamp ordering
        
        # Assert: All actions are queued
        assert queue_manager.get_queue_size() == len(actions), \
            f"Queue should contain {len(actions)} actions"
        
        # Assert: Actions are in correct order
        queued_actions = queue_manager._get_queue()
        for i, (action_id, original_action) in enumerate(zip(action_ids, actions)):
            assert queued_actions[i]['id'] == action_id
            assert queued_actions[i]['method'] == original_action['method']
            assert queued_actions[i]['url'] == original_action['url']
    
    @given(actions=offline_action_sequence_strategy())
    @settings(
        max_examples=200,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_queued_actions_sync_when_online(self, actions):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Property: For any queued actions, when connectivity is restored,
        the system should synchronize all queued actions with the server.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        api_client = MockAPIClient()
        
        # Queue actions while offline
        queue_manager.set_online_status(False)
        for action in actions:
            queue_manager.queue_action(
                method=action['method'],
                url=action['url'],
                body=action['body'],
                headers=action['headers']
            )
        
        initial_queue_size = queue_manager.get_queue_size()
        assert initial_queue_size == len(actions)
        
        # Act: Come back online and process queue
        queue_manager.set_online_status(True)
        result = queue_manager.process_queue(api_client)
        
        # Assert: All actions were processed
        assert result['processed'] == len(actions), \
            f"Expected {len(actions)} actions processed, got {result['processed']}"
        assert result['failed'] == 0, "No actions should fail"
        assert result['remaining'] == 0, "Queue should be empty after sync"
        
        # Assert: API client received all requests
        assert api_client.get_requests_count() == len(actions), \
            f"API client should receive {len(actions)} requests"
        
        # Assert: Queue is empty after successful sync
        assert queue_manager.get_queue_size() == 0, "Queue should be empty"
    
    @given(conflict=conflict_scenario_strategy())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_conflict_resolution_last_write_wins(self, conflict):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Property: For any resource modified both offline and online, when syncing,
        the system should resolve conflicts using last-write-wins strategy.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        api_client = MockAPIClient()
        
        resource_id = conflict['resource_id']
        offline_action = conflict['offline_action']
        online_action = conflict['online_action']
        
        # Simulate online modification happening first
        api_client.request(
            method=online_action['method'],
            url=online_action['url'],
            body=online_action['body']
        )
        
        # Queue offline modification
        queue_manager.set_online_status(False)
        queue_manager.queue_action(
            method=offline_action['method'],
            url=offline_action['url'],
            body=offline_action['body']
        )
        
        # Act: Come back online and sync (offline action syncs after online action)
        queue_manager.set_online_status(True)
        result = queue_manager.process_queue(api_client)
        
        # Assert: Sync completed successfully
        assert result['processed'] == 1, "Offline action should be processed"
        assert result['failed'] == 0, "No conflicts should cause failures"
        
        # Assert: Last write wins - offline action overwrites online action
        # (because offline action syncs after online action)
        final_data = api_client.server_data.get(str(resource_id))
        assert final_data is not None, "Resource should exist on server"
        
        # The last write (offline action synced) should win
        assert final_data['notes'] == offline_action['body']['notes'], \
            "Last write (offline action) should win conflict resolution"
    
    @given(actions=offline_action_sequence_strategy())
    @settings(
        max_examples=100,
        deadline=15000,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_failed_sync_retries_with_max_limit(self, actions):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Property: For any queued action that fails to sync, the system should
        retry up to MAX_RETRIES times before discarding the action.
        """
        assume(len(actions) > 0)
        
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        api_client = MockAPIClient()
        api_client.should_fail = True  # Simulate API failures
        
        # Queue actions while offline
        queue_manager.set_online_status(False)
        for action in actions:
            queue_manager.queue_action(
                method=action['method'],
                url=action['url'],
                body=action['body'],
                headers=action['headers']
            )
        
        initial_queue_size = queue_manager.get_queue_size()
        
        # Act: Try to sync multiple times (up to MAX_RETRIES)
        queue_manager.set_online_status(True)
        
        for retry in range(queue_manager.MAX_RETRIES):
            result = queue_manager.process_queue(api_client)
            
            if retry < queue_manager.MAX_RETRIES - 1:
                # Actions should remain in queue for retry
                assert result['remaining'] == initial_queue_size, \
                    f"After retry {retry + 1}, all actions should remain in queue"
            else:
                # After MAX_RETRIES, actions should be discarded
                assert result['failed'] == initial_queue_size, \
                    f"After {queue_manager.MAX_RETRIES} retries, all actions should be marked as failed"
                assert result['remaining'] == 0, \
                    "Queue should be empty after max retries"
        
        # Assert: Queue is empty after max retries
        assert queue_manager.get_queue_size() == 0, \
            "Queue should be empty after exceeding max retries"
    
    def test_queue_persistence_across_sessions(self):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Test that queued actions persist across app sessions (simulated by
        creating new queue manager instances with same storage).
        """
        # Arrange
        storage = OfflineQueueStorage()
        
        # Session 1: Queue actions
        queue_manager_1 = OfflineQueueManager(storage)
        queue_manager_1.set_online_status(False)
        
        action_1 = {
            'method': 'POST',
            'url': '/farms',
            'body': {'name': 'Test Farm 1', 'state': 'Punjab'},
            'headers': {}
        }
        action_2 = {
            'method': 'POST',
            'url': '/crops',
            'body': {'crop_type': 'wheat', 'area': 10.0},
            'headers': {}
        }
        
        queue_manager_1.queue_action(**action_1)
        queue_manager_1.queue_action(**action_2)
        
        assert queue_manager_1.get_queue_size() == 2
        
        # Session 2: New queue manager instance with same storage
        queue_manager_2 = OfflineQueueManager(storage)
        
        # Assert: Queue persists across sessions
        assert queue_manager_2.get_queue_size() == 2, \
            "Queue should persist across sessions"
        
        # Assert: Actions are intact
        queued_actions = queue_manager_2._get_queue()
        assert queued_actions[0]['url'] == action_1['url']
        assert queued_actions[1]['url'] == action_2['url']
    
    def test_queue_cleared_after_successful_sync(self):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Test that the queue is cleared after all actions are successfully synced.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        api_client = MockAPIClient()
        
        # Queue actions while offline
        queue_manager.set_online_status(False)
        queue_manager.queue_action(
            method='POST',
            url='/farms',
            body={'name': 'Test Farm', 'state': 'Punjab'}
        )
        queue_manager.queue_action(
            method='POST',
            url='/crops',
            body={'crop_type': 'wheat', 'area': 10.0}
        )
        
        assert queue_manager.get_queue_size() == 2
        
        # Act: Come online and sync
        queue_manager.set_online_status(True)
        result = queue_manager.process_queue(api_client)
        
        # Assert: Queue is cleared
        assert result['processed'] == 2
        assert result['remaining'] == 0
        assert queue_manager.get_queue_size() == 0
        
        # Assert: Storage is cleared
        assert storage.get_item(queue_manager.QUEUE_KEY) == '[]'
    
    def test_no_sync_when_offline(self):
        """
        **Validates: Requirements (Non-Functional - Offline Functionality)**
        
        Test that queued actions are not synced when the system is offline.
        """
        # Arrange
        storage = OfflineQueueStorage()
        queue_manager = OfflineQueueManager(storage)
        api_client = MockAPIClient()
        
        # Queue actions while offline
        queue_manager.set_online_status(False)
        queue_manager.queue_action(
            method='POST',
            url='/farms',
            body={'name': 'Test Farm', 'state': 'Punjab'}
        )
        
        initial_queue_size = queue_manager.get_queue_size()
        
        # Act: Try to process queue while still offline
        result = queue_manager.process_queue(api_client)
        
        # Assert: No actions processed
        assert result['status'] == 'offline'
        assert result['processed'] == 0
        assert result['remaining'] == initial_queue_size
        
        # Assert: Queue unchanged
        assert queue_manager.get_queue_size() == initial_queue_size
        
        # Assert: No API requests made
        assert api_client.get_requests_count() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
