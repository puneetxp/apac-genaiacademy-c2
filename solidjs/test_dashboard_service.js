// Quick test to verify DashboardService exports
import { DashboardService } from './src/services/dashboard.service.ts';

console.log('DashboardService:', DashboardService);
console.log('getProfileStatus:', DashboardService.getProfileStatus);
console.log('getDashboardData:', DashboardService.getDashboardData);

if (typeof DashboardService.getProfileStatus === 'function') {
  console.log('✓ getProfileStatus is a function');
} else {
  console.log('✗ getProfileStatus is NOT a function');
}
