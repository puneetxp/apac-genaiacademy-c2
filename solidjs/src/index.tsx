/* @refresh reload */
import { render } from 'solid-js/web';
import { Router, Route } from '@solidjs/router';
import { lazy, Component, onMount, Suspense } from 'solid-js';
import { useNavigate } from '@solidjs/router';
import App from './App';
import Home from './pages/Home';
import ProtectedRoute from './components/ProtectedRoute';
import './assets/styles/index.css';

// Lazy load pages
const SignUpPage = lazy(() => import('./pages/auth/SignUp'));
const SignInPage = lazy(() => import('./pages/auth/SignIn'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AssistantChat = lazy(() => import('./pages/Assistant'));
const FarmRegisterPage = lazy(() => import('./pages/farm/Register'));
const FarmDashboardPage = lazy(() => import('./pages/farm/FarmDashboard'));
const StrategyRequestPage = lazy(() => import('./pages/strategy/Request'));
const StrategySelectFarmPage = lazy(() => import('./pages/strategy/SelectFarm'));
const StrategyResultsPage = lazy(() => import('./pages/strategy/Results'));
const QuotaHistoryPage = lazy(() => import('./pages/quota/QuotaHistory').then((m) => ({ default: m.QuotaHistory })));
const BuyerDashboardPage = lazy(() => import('./pages/marketplace/BuyerDashboard'));
const LivestockMarketplaceBrowsePage = lazy(() => import('./pages/livestock-marketplace/Browse'));
const MarketplaceBrowsePage = lazy(() => import('./pages/marketplace/Browse'));
const MyListingsPage = lazy(() => import('./pages/marketplace/MyListings'));
const ListingDetailPage = lazy(() => import('./pages/marketplace/Detail'));
const BookingsPage = lazy(() => import('./pages/marketplace/Bookings'));
const BookingDetailsPage = lazy(() => import('./pages/marketplace/BookingDetails'));
const MarketIntelligencePage = lazy(() => import('./pages/marketplace/MarketIntelligence'));
const SupplyPlanningPage = lazy(() => import('./pages/marketplace/SupplyPlanning'));
const PlatformAnalyticsPage = lazy(() => import('./pages/admin/PlatformAnalytics'));
const PlotAnalyzePage = lazy(() => import('./pages/plots/Analyze'));
const PlotComparePage = lazy(() => import('./pages/plots/Compare'));
const PlotCreatePage = lazy(() => import('./pages/plots/Create'));
const FarmAnalyticsPage = lazy(() => import('./pages/farm/FarmAnalytics'));
const PlantCropPage = lazy(() => import('./pages/crops/PlantCrop'));
const AnnualStrategyDetailPage = lazy(() => import('./pages/crops/AnnualStrategyDetail'));
const FarmPage = lazy(() => import('./pages/farm/Index'));
const MyCropsPage = lazy(() => import('./pages/crops/MyCrops'));
const ProfilePage = lazy(() => import('./pages/users/Profile'));
const SecurityPage = lazy(() => import('./pages/users/Security'));
const ClimateHubPage = lazy(() => import('./pages/climate/ClimateHub'));
const SoilFertilizerHubPage = lazy(() => import('./pages/soil/SoilFertilizerHub'));
const PestDiseaseHubPage = lazy(() => import('./pages/pest-disease/PestDiseaseHub'));
const LivestockHubPage = lazy(() => import('./pages/livestock/LivestockHub'));
const VeterinaryDoctorsPage = lazy(() => import('./pages/livestock/VeterinaryDoctors'));
const PashuHomePage = lazy(() => import('./pages/livestock/PashuHome'));
const AllServicesPage = lazy(() => import('./pages/AllServices'));
const ConfigurationPage = lazy(() => import('./pages/Configuration'));
const DietPlanPage = lazy(() => import('./pages/livestock/DietPlan'));
const ServicesDirectoryPage = lazy(() => import('./pages/services/ServicesDirectory'));
const TransportTrackingPage = lazy(() => import('./pages/transport/TransportTracking'));
const NotificationsPage = lazy(() => import('./pages/notifications/Notifications'));


// Wrapper components for protected routes
const DashboardPage: Component = () => <ProtectedRoute><Dashboard /></ProtectedRoute>;
const AssistantPage: Component = () => <ProtectedRoute><AssistantChat /></ProtectedRoute>;
const FarmRegisterPageWrapped: Component = () => <ProtectedRoute><FarmRegisterPage /></ProtectedRoute>;
const FarmDashboardPageWrapped: Component = () => <ProtectedRoute><FarmDashboardPage /></ProtectedRoute>;
const StrategyRequestPageWrapped: Component = () => <ProtectedRoute><StrategyRequestPage /></ProtectedRoute>;
const StrategySelectFarmPageWrapped: Component = () => <ProtectedRoute><StrategySelectFarmPage /></ProtectedRoute>;
const StrategyResultsPageWrapped: Component = () => <ProtectedRoute><StrategyResultsPage /></ProtectedRoute>;
const QuotaHistoryPageWrapped: Component = () => <ProtectedRoute><QuotaHistoryPage /></ProtectedRoute>;
const BuyerDashboardPageWrapped: Component = () => <ProtectedRoute><BuyerDashboardPage /></ProtectedRoute>;
const LivestockMarketplaceBrowsePageWrapped: Component = () => <ProtectedRoute><LivestockMarketplaceBrowsePage /></ProtectedRoute>;
const MyListingsPageWrapped: Component = () => <ProtectedRoute><MyListingsPage /></ProtectedRoute>;
const BookingsPageWrapped: Component = () => <ProtectedRoute><BookingsPage /></ProtectedRoute>;
const BookingDetailsPageWrapped: Component = () => <ProtectedRoute><BookingDetailsPage /></ProtectedRoute>;
const MarketIntelligencePageWrapped: Component = () => <ProtectedRoute><MarketIntelligencePage /></ProtectedRoute>;
const SupplyPlanningPageWrapped: Component = () => <ProtectedRoute><SupplyPlanningPage /></ProtectedRoute>;
const PlatformAnalyticsPageWrapped: Component = () => <ProtectedRoute><PlatformAnalyticsPage /></ProtectedRoute>;
const PlotAnalyzePageWrapped: Component = () => <ProtectedRoute><PlotAnalyzePage /></ProtectedRoute>;
const PlotComparePageWrapped: Component = () => <ProtectedRoute><PlotComparePage /></ProtectedRoute>;
const PlotCreatePageWrapped: Component = () => <ProtectedRoute><PlotCreatePage /></ProtectedRoute>;
const FarmAnalyticsPageWrapped: Component = () => <ProtectedRoute><FarmAnalyticsPage /></ProtectedRoute>;
const PlantCropPageWrapped: Component = () => <ProtectedRoute><PlantCropPage /></ProtectedRoute>;
const AnnualStrategyDetailPageWrapped: Component = () => <ProtectedRoute><AnnualStrategyDetailPage /></ProtectedRoute>;
const FarmPageWrapped: Component = () => <ProtectedRoute><FarmPage /></ProtectedRoute>;
const MyCropsPageWrapped: Component = () => <ProtectedRoute><MyCropsPage /></ProtectedRoute>;
const ProfilePageWrapped: Component = () => <ProtectedRoute><ProfilePage /></ProtectedRoute>;
const SecurityPageWrapped: Component = () => <ProtectedRoute><SecurityPage /></ProtectedRoute>;
const ClimateHubPageWrapped: Component = () => <ProtectedRoute><ClimateHubPage /></ProtectedRoute>;
const SoilFertilizerHubPageWrapped: Component = () => <ProtectedRoute><SoilFertilizerHubPage /></ProtectedRoute>;
const PestDiseaseHubPageWrapped: Component = () => <ProtectedRoute><PestDiseaseHubPage /></ProtectedRoute>;
const LivestockHubPageWrapped: Component = () => <ProtectedRoute><LivestockHubPage /></ProtectedRoute>;
const VeterinaryDoctorsPageWrapped: Component = () => <ProtectedRoute><VeterinaryDoctorsPage /></ProtectedRoute>;
const PashuHomePageWrapped: Component = () => <ProtectedRoute><PashuHomePage /></ProtectedRoute>;
const AllServicesPageWrapped: Component = () => <ProtectedRoute><AllServicesPage /></ProtectedRoute>;
const ConfigurationPageWrapped: Component = () => <ProtectedRoute><ConfigurationPage /></ProtectedRoute>;
const DietPlanPageWrapped: Component = () => <ProtectedRoute><DietPlanPage /></ProtectedRoute>;
const ServicesDirectoryPageWrapped: Component = () => <ProtectedRoute><ServicesDirectoryPage /></ProtectedRoute>;
const TransportTrackingPageWrapped: Component = () => <ProtectedRoute><TransportTrackingPage /></ProtectedRoute>;
const NotificationsPageWrapped: Component = () => <ProtectedRoute><NotificationsPage /></ProtectedRoute>;



// Redirect component for /crops/plan -> /strategy/select-farm
const CropsPlanRedirect: Component = () => {
  const navigate = useNavigate();

  onMount(() => {
    navigate('/strategy/select-farm', { replace: true });
  });

  return null;
};

const CropsPlanRedirectWrapped: Component = () => <ProtectedRoute><CropsPlanRedirect /></ProtectedRoute>;

const root = document.getElementById('root');

if (import.meta.env.DEV && !(root instanceof HTMLElement)) {
  throw new Error(
    'Root element not found. Did you forget to add it to your index.html? Or maybe the id attribute got misspelled?',
  );
}

render(
  () => (
    <Router root={App}>
      <Route path="/" component={Home} />
      <Route path="/auth/signup" component={SignUpPage} />
      <Route path="/auth/signin" component={SignInPage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/assistant" component={AssistantPage} />
      <Route path="/farm" component={FarmPageWrapped} />
      <Route path="/farm/register" component={FarmRegisterPageWrapped} />
      <Route path="/farm/:id" component={FarmDashboardPageWrapped} />
      <Route path="/crops/plan" component={CropsPlanRedirectWrapped} />
      <Route path="/crops/plant" component={PlantCropPageWrapped} />
      <Route path="/crops/my-crops" component={MyCropsPageWrapped} />
      <Route path="/crops/annual-strategy/:id" component={AnnualStrategyDetailPageWrapped} />

      <Route path="/strategy/select-farm" component={StrategySelectFarmPageWrapped} />
      <Route path="/strategy/results" component={StrategyResultsPageWrapped} />
      <Route path="/quota/history" component={QuotaHistoryPageWrapped} />
      <Route path="/marketplace/buyer-dashboard" component={BuyerDashboardPageWrapped} />
      <Route path="/livestock-marketplace" component={LivestockMarketplaceBrowsePageWrapped} />
      <Route path="/strategy/request" component={StrategyRequestPageWrapped} />
      <Route path="/plots/analyze" component={PlotAnalyzePageWrapped} />
      <Route path="/plots/compare" component={PlotComparePageWrapped} />
      <Route path="/plots/create" component={PlotCreatePageWrapped} />
      <Route path="/marketplace" component={MarketplaceBrowsePage} />
      <Route path="/marketplace/my-listings" component={MyListingsPageWrapped} />
      <Route path="/marketplace/:id" component={ListingDetailPage} />
      <Route path="/marketplace/bookings" component={BookingsPageWrapped} />
      <Route path="/marketplace/bookings/:id" component={BookingDetailsPageWrapped} />
      <Route path="/marketplace/intelligence" component={MarketIntelligencePageWrapped} />
      <Route path="/marketplace/supply-planning" component={SupplyPlanningPageWrapped} />
      <Route path="/admin/analytics" component={PlatformAnalyticsPageWrapped} />
      <Route path="/analytics/farm/:id" component={FarmAnalyticsPageWrapped} />

      <Route path="/users/profile" component={ProfilePageWrapped} />
      <Route path="/users/security" component={SecurityPageWrapped} />
      <Route path="/climate/hub" component={ClimateHubPageWrapped} />
      <Route path="/soil/hub" component={SoilFertilizerHubPageWrapped} />
      <Route path="/pest-disease/hub" component={PestDiseaseHubPageWrapped} />
      <Route path="/livestock" component={PashuHomePageWrapped} />
      <Route path="/menu" component={AllServicesPageWrapped} />
      <Route path="/settings" component={ConfigurationPageWrapped} />
      <Route path="/livestock/diet-plan" component={DietPlanPageWrapped} />
      <Route path="/services" component={ServicesDirectoryPageWrapped} />
      <Route path="/livestock/hub" component={LivestockHubPageWrapped} />
      <Route path="/livestock/doctors" component={VeterinaryDoctorsPageWrapped} />
      <Route path="/transport/tracking" component={TransportTrackingPageWrapped} />
      <Route path="/notifications" component={NotificationsPageWrapped} />

    </Router>
  ),
  root!
);
