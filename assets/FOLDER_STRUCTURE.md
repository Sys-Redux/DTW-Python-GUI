# 📁 Assets Folder Structure

After adding your sprite images, your folder should look like this:

```
pygame/
├── battlewiz.py
├── DTW.py
├── README.md
└── assets/
    ├── ASSET_GUIDE.md         ← Detailed instructions (you're here!)
    ├── QUICK_START.md         ← Quick 5-minute guide
    ├── warrior.png            ← Add this! (your warrior sprite)
    ├── mage.png               ← Add this! (your mage sprite)
    ├── archer.png             ← Add this! (your archer sprite)
    ├── paladin.png            ← Add this! (your paladin sprite)
    ├── wizard.png             ← Add this! (evil wizard sprite)
    └── battle_bg.png          ← Optional! (battle background)
```

## ✅ Checklist

After downloading sprites, make sure you have:
- [ ] `warrior.png` - Warrior character image
- [ ] `mage.png` - Mage character image
- [ ] `archer.png` - Archer character image
- [ ] `paladin.png` - Paladin character image
- [ ] `wizard.png` - Evil Wizard enemy image
- [ ] `battle_bg.png` - (Optional) Battle background

## 🎮 What Happens When You Add Sprites

### Without Custom Sprites (Default):
```
💡 NO CUSTOM SPRITES FOUND - Using drawn sprites
```
The game uses the built-in drawn graphics (simple shapes).

### With Custom Sprites:
```
✓ Loaded warrior.png
✓ Loaded mage.png
✓ Loaded archer.png
✓ Loaded paladin.png
✓ Loaded wizard.png
✓ Loaded battle_bg.png
```
The game uses YOUR images for these characters!

### Partial Sprites (Mix & Match):
```
✓ Loaded warrior.png
✓ Loaded wizard.png
```
The game uses your warrior and wizard images, but draws the others!

You can add sprites one at a time - no need to do them all at once!

## 🖼️ Image Format Tips

### Good Image:
- ✅ PNG format
- ✅ Transparent background
- ✅ Square-ish dimensions (100x100, 128x128, 200x200)
- ✅ Character centered in image
- ✅ Clear, visible details

### Not Ideal:
- ❌ JPG format (no transparency)
- ❌ White/colored background
- ❌ Extremely rectangular (1000x100)
- ❌ Character off-center
- ❌ Too small (under 50x50) or too large (over 1000x1000)

## 🔧 Troubleshooting

### "Failed to load [filename].png"
- Check: Is the file actually a PNG?
- Check: Is the filename spelled exactly right? (lowercase)
- Check: Is the file in the `assets` folder?

### Sprite looks stretched or squished
- Use square images for best results
- Game auto-scales to 100px for player, 80px for wizard

### Transparent background not working
- Make sure the PNG has an alpha channel
- Open in image editor and re-save as PNG with transparency

### Background image looks weird
- Background should ideally be 800x600 pixels
- Game will scale it to fit, but native size looks best

## 💬 Need Help?

1. Check that files are named EXACTLY as shown (lowercase, .png extension)
2. Make sure files are actually PNG format (not JPG renamed)
3. Try adding just one sprite first to test
4. Check console output when game starts for error messages
