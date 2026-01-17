# Quick Start Guide - 19" Rack Mount Generator

## 5-Minute Setup

### Step 1: Install Python & uv
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Install uv package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
4. Verify installation:
   ```bash
   python --version
   uv --version
   ```

### Step 2: Clone or Extract Files
```bash
git clone https://github.com/leprachuan/rack-mount-generator.git
cd rack-mount-generator
```

### Step 3: Run the Application

**Using uv (recommended):**
```bash
uv sync
uv run python app.py
```

**Using pip:**
```bash
pip install -r requirements.txt
python app.py
```

The server will:
- ✓ Start Flask on port 5001
- ✓ Serve the web interface

### Step 4: Open in Browser
Navigate to: **http://localhost:5001**

> **Note**: Port 5001 is used because 5000 is often blocked on macOS.

You should see the 19" Rack Mount Generator interface!

---

## First Generation (2 Minutes)

### Enter Device Dimensions
Let's say you want to mount a network switch that's:
- **Width**: 100 mm
- **Height**: 44 mm (1U standard)
- **Depth**: 200 mm

1. Enter these values in the form
2. Keep default settings (2mm tolerance, 10mm wall thickness)
3. Enable options:
   - ✓ Add Support Shelf
   - ✓ Add Rack Holes
4. Click **"Generate STL Files"**

### Download Files
The STL file downloads automatically - what you see in the preview is exactly what you get!

---

## Printing (At Your 3D Printer)

### What You'll Need
- **3D Printer** (any FDM printer - Prusa, Ender 3, etc.)
- **Filament** (PLA recommended, PETG for strength)
- **Slicing Software** (Cura, PrusaSlicer, etc.)

### Steps

1. **Download and Install Slicer**
   - [Cura](https://ultimaker.com/software/ultimaker-cura) (Free, easy to use)
   - [PrusaSlicer](https://www.prusa3d.com/en/prusaslicer/) (Great for Prusa printers)

2. **Open STL File in Slicer**
   - Launch your slicer
   - Open the downloaded `rack_mount_*.stl` file
   - Position: Flat side down (already optimized)

3. **Configure Print Settings**
   - **Infill**: 20%
   - **Layer Height**: 0.2mm (standard)
   - **Nozzle**: 0.4mm
   - **Support**: Off (not needed)

4. **Export and Print**
   - Save as G-code
   - Transfer to printer
   - Start print!

5. **Repeat for Other Parts**
   - Print `bracket_right.stl`
   - Print `retention_clip.stl`

### Estimated Print Times
- Each bracket: 4-8 hours (100×44×200mm device)
- Retention clip: 1-2 hours
- **Total: 9-18 hours** (depending on printer speed)

---

## Assembly (15 Minutes)

### You'll Need
- All 3 printed parts
- M6 bolts and nuts (or 1/4" equivalent)
- Your device to mount
- Small Allen wrench

### Instructions

1. **Inspect Parts**
   - Look for any defects
   - Sand smooth any rough edges

2. **Check Alignment**
   - Place device in bracket cavity
   - Should slide in smoothly with 2mm clearance
   - If too tight, warm brackets with hot water for 2 minutes

3. **Assemble in Rack**
   - Position left bracket in rack
   - Slide device into bracket
   - Position right bracket on other side
   - Snap retention clip on front

4. **Secure Bolts**
   - Use M6 bolts through bracket mounting holes
   - Tighten securely (not over-tight)
   - Check that device doesn't move

---

## Customization

### Want Different Clearance?
If your device is too tight:
- Reduce tolerance from 2mm to 1mm
- Regenerate and reprint

If your device is too loose:
- Increase tolerance from 2mm to 3-5mm
- Regenerate and reprint

### Want Stronger Brackets?
- Increase **Wall Thickness** from 3mm to 4-5mm
- Increase **Infill** from 20% to 30-50%
- Reprint

### Want Different Device Size?
- Just change width, height, depth
- Keep everything else the same
- Click Generate!

---

## Troubleshooting

### "Python not found" error
- Python not in PATH
- **Fix**: Reinstall Python and check "Add Python to PATH"

### "Port 5000 already in use"
- Another application is using port 5000
- **Fix**: Close other applications or edit app.py to use different port

### 3D preview not showing
- WebGL not supported in your browser
- **Fix**: Use Chrome or Firefox (they have best WebGL support)

### STL file won't open in slicer
- File might be corrupted
- **Fix**: Regenerate the file
- Or try a different slicer

### Device doesn't fit in bracket
- Tolerance too small
- **Fix**: Increase tolerance and regenerate

---

## Tips & Tricks

### Save Time Printing
- Increase infill to only 15% (still strong enough)
- Saves ~25% print time
- Reduces filament cost

### Save Money on Filament
- Use cheaper PLA instead of PETG
- 15% infill is sufficient for light devices
- Check if printer manufacturer has deals

### Better Print Quality
- Use highest resolution (0.1mm layers)
- Takes longer but looks cleaner
- Good if mounting visible on desk

### Multiple Devices
- Save your configuration
- Generate once, print multiple times
- Stack brackets for different heights

---

## File Management

### Where Are My Files?
- Downloaded STL files are in your **Downloads** folder
- Web server stores files in temporary directory (auto-cleanup after 24h)

### Backup Your Configuration
- Save the config.json file from your job
- Reuse it later for reprints

### Re-Generate Old Designs
- Note the job ID (e.g., `20240115_143025`)
- Job files stored in `/tmp/rack_mounts/`
- Files auto-deleted after 24 hours (save them!)

---

## Next Steps

### Want More Features?
- Read `README.md` for complete documentation
- Check `DEVELOPMENT.md` for advanced customization
- Look at `test_generator.py` for examples

### Want to Contribute?
- Modify `stl_generator.py` to add new bracket types
- Update HTML form in `index.html` for new options
- Test with `test_generator.py`

### Having Issues?
- Run `test_generator.py` to verify installation
- Check browser console (F12) for JavaScript errors
- Review error messages in terminal

---

## Video Guide (Optional)

*Coming soon: Video walkthrough of the entire process*

---

## Common Questions

**Q: Will this work with my printer?**
A: Yes! Works with Prusa, Ender 3, CR-10, Anet, and almost all FDM printers. Just verify your bed size.

**Q: How strong is the mount?**
A: With 20% infill and 3mm walls, it safely supports devices up to 5-10kg depending on material.

**Q: Can I use different filament?**
A: Yes! PLA, PETG, ABS all work. PETG is stronger if you need extra durability.

**Q: What if my device isn't square?**
A: Current version designed for rectangular/square devices. For cylindrical, contact support or modify code.

**Q: How long does a bracket last?**
A: With proper installation, 2+ years minimum. PLA can become brittle in extreme heat (>60°C).

**Q: Can I remix/modify these files?**
A: Yes! Source code is yours to modify and improve.

---

## Support & Community

### Need Help?
1. Check this guide first
2. Review README.md for detailed docs
3. Check browser developer console (F12) for errors
4. Try `test_generator.py` to verify setup

### Found a Bug?
- Document what happened
- Include your device dimensions
- Screenshot of error message
- Steps to reproduce

### Have Ideas?
- Suggest new features
- Request printer profiles
- Share your creations!

---

## Resources

- **3D Printing Basics**: [YouTube - 3D Printing 101](https://www.youtube.com/)
- **STL Format Spec**: [3D Systems STL Documentation](https://www.3dsystems.com/)
- **Cura Tutorial**: [Ultimaker Cura Docs](https://ultimaker.com/software/ultimaker-cura/)
- **Fusion 360 (design your own)**: [Autodesk Fusion 360](https://www.autodesk.com/products/fusion-360/)

---

**You're all set!** 🎉

Now go print your first rack mount! Show us your creation.

---

*Last Updated: January 2024*
*Version: 1.0.0*
