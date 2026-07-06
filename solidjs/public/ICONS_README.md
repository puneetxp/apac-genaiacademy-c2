# PWA Icons

This directory should contain the following icon files for the Progressive Web App:

## Required Icons

- `icon-72.png` - 72x72 pixels
- `icon-96.png` - 96x96 pixels
- `icon-128.png` - 128x128 pixels
- `icon-144.png` - 144x144 pixels
- `icon-152.png` - 152x152 pixels
- `icon-192.png` - 192x192 pixels (required for PWA)
- `icon-384.png` - 384x384 pixels
- `icon-512.png` - 512x512 pixels (required for PWA)
- `badge-72.png` - 72x72 pixels (notification badge)

## Generating Icons

You can generate these icons from a single source image using:

1. **Online Tools:**
   - https://realfavicongenerator.net/
   - https://www.pwabuilder.com/imageGenerator

2. **Command Line:**
   ```bash
   # Using ImageMagick
   convert source-icon.png -resize 192x192 icon-192.png
   convert source-icon.png -resize 512x512 icon-512.png
   ```

3. **Design Guidelines:**
   - Use a square image (1:1 aspect ratio)
   - Minimum safe area: 80% of the icon (leave 10% padding on each side)
   - Use simple, recognizable imagery
   - Test on both light and dark backgrounds
   - Consider using a green color scheme to match the farming theme (#22c55e)

## Icon Design Suggestions

For the CropSense AI farming platform, consider:
- A stylized crop/plant icon
- A combination of technology (circuit/AI) and agriculture (leaf/crop)
- Simple, bold shapes that work at small sizes
- Green color palette (#22c55e primary, with earth tones)

## Temporary Solution

Until proper icons are created, you can:
1. Use the Vite default icon as a placeholder
2. Create simple colored squares with the app initials
3. Use a free icon from sources like:
   - https://www.flaticon.com/ (agriculture icons)
   - https://iconmonstr.com/
   - https://heroicons.com/
