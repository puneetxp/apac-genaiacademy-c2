# Demo Data Seeding Instructions

## 🎯 Purpose

Create comprehensive, realistic demo data for video recording using the **existing authenticated user** from global-setup.

## 📋 Prerequisites

1. **Backend running**: `http://localhost:8000`
2. **Frontend running**: `http://localhost:3000`
3. **Global setup completed**: `.auth/user.json` and `.auth/test-user.json` exist
4. **Test user authenticated**: Session saved from global-setup

## 🚀 Quick Start

```bash
cd rural-farming-platform/e2e

# Run data seeding test
npm test tests/00-seed-demo-data.spec.ts

# This will:
# 1. Use existing authenticated user
# 2. Create 3 farms with different characteristics
# 3. Create 8 plots with various soil types
# 4. Generate 3 AI crop strategies (Google Vertex AI)
# 5. Plant 8 crops in different growth stages
# 6. Create 4 marketplace listings
# 7. Add 5 livestock animals
# 8. Generate 5 buyer interests
# 9. Add 3 soil test records
```

## 📊 Data Created

### User
- **Uses existing test user** from global-setup
- Email: From `.auth/test-user.json`
- Already authenticated

### Farms (3)
1. **Green Valley Farm** - 5.5 acres, loamy soil, drip irrigation
2. **Sunrise Agricultural Land** - 3.2 acres, clay soil, sprinkler irrigation
3. **Golden Harvest Fields** - 8.0 acres, sandy loam, flood irrigation

### Plots (8)
- Farm 1: North Field, South Field, East Field
- Farm 2: Main Plot, Back Plot
- Farm 3: West Section, East Section, Central Section

### AI Crop Strategies (3)
- One comprehensive annual strategy per farm
- Generated using Google Vertex AI
- Includes Kharif, Rabi, Zaid seasons
- Profit estimates and confidence scores

### Crops (8 - Different Stages)
1. **Wheat** - Recently planted (germination)
2. **Rice** - Recently planted (germination)
3. **Corn** - Growing (vegetative)
4. **Cotton** - Growing (vegetative)
5. **Tomato** - Mature (flowering)
6. **Potato** - Mature (flowering)
7. **Wheat** - Ready for harvest (maturity)
8. **Mustard** - Ready for harvest (maturity)

### Marketplace Listings (4)
1. Wheat - 3500 kg, Grade A, ₹25/kg
2. Mustard - 1200 kg, Grade A, ₹60/kg
3. Tomato - 2000 kg, Grade B, ₹30/kg
4. Potato - 4000 kg, Grade A, ₹20/kg

### Livestock (5)
1. Holstein Cow - 3 years, dairy
2. Jersey Cow - 4 years, dairy
3. Murrah Buffalo - 5 years, dairy
4. Beetal Goat - 2 years, meat
5. Sirohi Goat - 1 year, breeding

### Buyer Interests (5)
- Multiple buyers for each listing
- Different quantity requirements
- Contact information included

### Soil Tests (3)
- Plot-specific soil analysis
- pH levels, NPK values
- Test dates recorded

## 🐛 Error Logging

All errors are logged to: `test-results/seed-data-errors.log`

**Error types captured:**
- Page JavaScript errors
- Console errors
- Failed HTTP requests
- Test step failures
- Element not found errors
- Timeout errors

**Log format:**
```
[2026-03-02T10:30:45.123Z] ERROR in Register farm 1: Element not found
Stack trace...

[2026-03-02T10:31:12.456Z] SUCCESS: Register farm 1 - Green Valley Farm
```

## 📹 After Seeding

Once data is seeded, you can:

1. **Record demo video**:
   ```bash
   npm test tests/demo-complete-workflow.spec.ts
   ```

2. **View data in UI**:
   - Open `http://localhost:3000`
   - Login with test user credentials
   - Browse farms, plots, crops, marketplace, livestock

3. **Check error log**:
   ```bash
   cat test-results/seed-data-errors.log
   ```

## 🔧 Troubleshooting

### Test user not found
```bash
# Run global setup first
npm test
```

### Authentication failed
```bash
# Delete auth files and re-run
rm -rf .auth/
npm test
```

### Seeding fails midway
- Check error log: `test-results/seed-data-errors.log`
- Test continues even if some steps fail
- Re-run to complete missing data

### Backend not responding
```bash
# Check backend is running
curl http://localhost:8000/health

# Restart if needed
cd ../python
uvicorn app.main:app --reload
```

### Frontend not responding
```bash
# Check frontend is running
curl http://localhost:3000

# Restart if needed
cd ../solidjs
npm run dev
```

## ⏱️ Duration

- **Total time**: 15-20 minutes
- **Farms**: 2-3 minutes
- **Plots**: 3-4 minutes
- **AI Strategies**: 5-6 minutes (Bedrock API calls)
- **Crops**: 2-3 minutes
- **Marketplace**: 2-3 minutes
- **Livestock**: 2-3 minutes
- **Buyer Interests**: 1-2 minutes

## 🎬 Ready for Demo

After seeding completes:

✅ Rich, realistic data in database  
✅ Multiple farms with different characteristics  
✅ Crops in various growth stages  
✅ AI-generated strategies visible  
✅ Active marketplace listings  
✅ Livestock portfolio populated  
✅ Buyer interests for engagement  

**Now record your demo video with professional-looking data!**

## 📝 Notes

- Test uses existing authenticated session (no login required)
- Continues even if some steps fail (resilient)
- All errors logged for debugging
- Data is realistic and varied for better demo
- Covers all major features of the platform

## 🔄 Re-running

To re-seed data:

```bash
# Option 1: Delete all data and re-seed
# (requires database reset)

# Option 2: Just run seeding again
# (will create duplicate data)
npm test tests/00-seed-demo-data.spec.ts

# Option 3: Seed with different user
# (create new test user first)
rm -rf .auth/
npm test  # Creates new user
npm test tests/00-seed-demo-data.spec.ts
```

## ✅ Success Criteria

Seeding is successful when:
- ✅ No critical errors in log
- ✅ At least 2 farms created
- ✅ At least 4 plots created
- ✅ At least 1 AI strategy generated
- ✅ At least 4 crops planted
- ✅ At least 2 marketplace listings
- ✅ Dashboard shows data

**Even with some errors, if you have data visible in the UI, you're ready for demo recording!**
