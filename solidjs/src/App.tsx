import { Component, onMount } from 'solid-js';
import BottomNav from './components/ui/BottomNav';
import DesktopServicesButton from './components/ui/DesktopServicesButton';
import MainNav from './components/ui/MainNav';
import InstallPrompt from './components/ui/InstallPrompt';
import OfflineIndicator from './components/ui/OfflineIndicator';
import ToastContainer from './components/ui/Toast';
import { initializeAuth } from './stores/auth.store';
import { initServiceWorker } from './utils/initServiceWorker';

const App: Component<{ children?: any }> = (props) => {
  // Initialize authentication and service worker on app load
  onMount(() => {
    initializeAuth();
    
    // Initialize service worker for push notifications and offline support
    initServiceWorker().catch((error) => {
      console.error('Failed to initialize service worker:', error);
    });
  });

  return (
    <div class="min-h-screen pb-safe-bottom">
      {/* <MainNav /> */}
      <ToastContainer />
      <OfflineIndicator />
      <InstallPrompt />
      <BottomNav />
      <DesktopServicesButton />
      {props.children}
    </div>
  );
};

export default App;
