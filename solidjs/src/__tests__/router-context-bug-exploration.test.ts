/**
 * Bug Condition Exploration Test for Router Context Error
 * 
 * **Validates: Requirements 1.1, 1.2, 1.3**
 * 
 * **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
 * 
 * **Bug Condition**: 
 * - App.tsx imports Route and Routes from 'the-solid-router'
 * - Components import router primitives from '@solidjs/router'
 * - Both packages are installed, creating two separate routing contexts
 * 
 * **Expected Behavior (after fix)**:
 * - All router primitives should work without context errors
 * - Single consistent router library across the application
 * 
 * **GOAL**: Surface counterexamples that demonstrate the router context bug exists
 * 
 * **Test Approach**: 
 * This test verifies the bug condition by checking:
 * 1. Both router packages exist in package.json (root cause)
 * 2. App.tsx imports from 'the-solid-router' (implementation detail)
 * 3. Components import from '@solidjs/router' (implementation detail)
 * 
 * When these conditions are true, the router context error occurs at runtime.
 */

import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

describe('Router Context Bug Exploration', () => {
  describe('Property 1: Fault Condition - Router Context Availability', () => {
    it('should verify both router packages are installed (root cause of bug)', () => {
      // Read package.json to check for conflicting router packages
      const packageJsonPath = join(__dirname, '../../package.json');
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));
      
      const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
      
      const hasSolidJsRouter = '@solidjs/router' in dependencies;
      const hasTheSolidRouter = 'the-solid-router' in dependencies;
      
      // Document the bug condition
      console.log('\n=== Bug Condition Analysis ===');
      console.log(`@solidjs/router installed: ${hasSolidJsRouter}`);
      console.log(`the-solid-router installed: ${hasTheSolidRouter}`);
      
      if (hasSolidJsRouter && hasTheSolidRouter) {
        console.log('\n❌ COUNTEREXAMPLE FOUND: Both router packages are installed!');
        console.log('This creates two separate routing contexts that cannot communicate.');
        console.log('Components using @solidjs/router primitives will throw:');
        console.log('"<A> and \'use\' router primitives can be only used inside a Route"');
      }
      
      // Expected after fix: only @solidjs/router should exist
      // On UNFIXED code: this assertion will FAIL (proving bug exists)
      // On FIXED code: this assertion will PASS (proving bug is fixed)
      expect(hasSolidJsRouter).toBe(true);
      expect(hasTheSolidRouter).toBe(false);
    });

    it('should verify App.tsx imports from correct router package', () => {
      // Read App.tsx to check import statement
      const appTsxPath = join(__dirname, '../App.tsx');
      const appTsxContent = readFileSync(appTsxPath, 'utf-8');
      
      // Check for imports from both packages
      const importsFromSolidJsRouter = appTsxContent.includes("from '@solidjs/router'");
      const importsFromTheSolidRouter = appTsxContent.includes("from 'the-solid-router'");
      
      console.log('\n=== App.tsx Import Analysis ===');
      console.log(`Imports from @solidjs/router: ${importsFromSolidJsRouter}`);
      console.log(`Imports from the-solid-router: ${importsFromTheSolidRouter}`);
      
      if (importsFromTheSolidRouter) {
        console.log('\n❌ COUNTEREXAMPLE FOUND: App.tsx imports from the-solid-router!');
        console.log('This creates a routing context that is incompatible with @solidjs/router.');
        
        // Extract the import line for documentation
        const importLine = appTsxContent.split('\n').find(line => 
          line.includes('the-solid-router')
        );
        console.log(`Import statement: ${importLine?.trim()}`);
      }
      
      // Expected after fix: App.tsx should import from @solidjs/router
      // On UNFIXED code: this assertion will FAIL (proving bug exists)
      // On FIXED code: this assertion will PASS (proving bug is fixed)
      expect(importsFromSolidJsRouter).toBe(true);
      expect(importsFromTheSolidRouter).toBe(false);
    });

    it('should verify components import from @solidjs/router (expected behavior)', () => {
      // Check a sample component that uses router primitives
      const componentPaths = [
        '../pages/strategy/Request.tsx',
        '../pages/marketplace/Bookings.tsx',
        '../pages/marketplace/BookingDetails.tsx',
        '../components/marketplace/MarketIntelligenceNav.tsx',
      ];
      
      console.log('\n=== Component Import Analysis ===');
      
      let allComponentsUseCorrectImport = true;
      const counterexamples: string[] = [];
      
      for (const componentPath of componentPaths) {
        try {
          const fullPath = join(__dirname, componentPath);
          const content = readFileSync(fullPath, 'utf-8');
          
          const usesNavigate = content.includes('useNavigate');
          const usesParams = content.includes('useParams');
          const usesSearchParams = content.includes('useSearchParams');
          const usesAComponent = content.includes('<A ') || content.includes('<A>');
          
          const importsFromSolidJsRouter = content.includes("from '@solidjs/router'");
          
          if ((usesNavigate || usesParams || usesSearchParams || usesAComponent) && importsFromSolidJsRouter) {
            console.log(`✓ ${componentPath}: Correctly imports from @solidjs/router`);
          } else if (usesNavigate || usesParams || usesSearchParams || usesAComponent) {
            console.log(`✗ ${componentPath}: Uses router primitives but imports from wrong package`);
            allComponentsUseCorrectImport = false;
            counterexamples.push(componentPath);
          }
        } catch (error) {
          // Component file might not exist, skip
        }
      }
      
      if (counterexamples.length > 0) {
        console.log('\n❌ COUNTEREXAMPLES: Components with incorrect imports:');
        counterexamples.forEach(path => console.log(`  - ${path}`));
      }
      
      // This should pass - components correctly import from @solidjs/router
      // The bug is that App.tsx imports from the-solid-router, creating context mismatch
      expect(allComponentsUseCorrectImport).toBe(true);
    });

    it('should document the complete bug condition', () => {
      // This test documents all three parts of the bug condition
      const packageJsonPath = join(__dirname, '../../package.json');
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf-8'));
      const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies };
      
      const appTsxPath = join(__dirname, '../App.tsx');
      const appTsxContent = readFileSync(appTsxPath, 'utf-8');
      
      const bugCondition = {
        bothPackagesInstalled: '@solidjs/router' in dependencies && 'the-solid-router' in dependencies,
        appImportsFromTheSolidRouter: appTsxContent.includes("from 'the-solid-router'"),
        componentsImportFromSolidJsRouter: true, // Verified in previous test
      };
      
      console.log('\n=== Complete Bug Condition ===');
      console.log(JSON.stringify(bugCondition, null, 2));
      
      if (bugCondition.bothPackagesInstalled && 
          bugCondition.appImportsFromTheSolidRouter && 
          bugCondition.componentsImportFromSolidJsRouter) {
        console.log('\n❌ ALL BUG CONDITIONS ARE MET!');
        console.log('\nRuntime Error Expected:');
        console.log('  "Uncaught (in promise) Error: <A> and \'use\' router primitives');
        console.log('   can be only used inside a Route"');
        console.log('\nRoot Cause:');
        console.log('  - App.tsx creates routing context using the-solid-router');
        console.log('  - Components try to access routing context from @solidjs/router');
        console.log('  - These are two separate contexts that cannot communicate');
        console.log('\nCounterexamples (router primitives that will fail):');
        console.log('  - useNavigate() from @solidjs/router');
        console.log('  - useParams() from @solidjs/router');
        console.log('  - useSearchParams() from @solidjs/router');
        console.log('  - <A> component from @solidjs/router');
      }
      
      // Expected after fix: bug conditions should NOT all be met
      // On UNFIXED code: this assertion will FAIL (proving bug exists)
      // On FIXED code: this assertion will PASS (proving bug is fixed)
      const bugExists = bugCondition.bothPackagesInstalled && 
                       bugCondition.appImportsFromTheSolidRouter;
      expect(bugExists).toBe(false);
    });
  });
});
