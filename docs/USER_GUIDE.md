# Business Unit Manager - User Guide

**Quick Start Guide for End Users**

---

## Accessing the Application

### Step 1: Login to Snowsight
1. Open your Snowflake account URL
2. Enter your credentials
3. Login to Snowsight interface

### Step 2: Navigate to Streamlit Apps
1. Click **"Projects"** in the left sidebar
2. Select **"Streamlit"**
3. Find and click **"BUSINESS_UNIT_MANAGER"**

The application will open in a new view.

---

## Understanding the Interface

### Header Section
- **Title**: Business Unit Manager 🏢
- **Mode Indicator**: 
  - 🔒 **Green "BACKUP MODE"** - Safe testing environment (current)
  - ⚠️ **Red "PRODUCTION MODE"** - Live data (future)
- **Last Refresh**: Shows when data was last loaded

### Sidebar (Left Panel)
- **Select Table**: Choose between Business Unit Details or Web Names
- **Search Records**: Type to filter records in real-time
- **Refresh Button**: Reload data from database
- **Clear Button**: Reset all selections and filters

### Main Area
- **Data Table**: Display of all records
- **Record Count**: Shows how many records are displayed
- **Selection Dropdown**: Choose a record to edit
- **Edit Form**: Appears when a record is selected

---

## How to Use

### Viewing Records

1. **Select a Table**
   - Use sidebar radio button
   - Choose "Business Unit Details" or "Web Names"

2. **Browse Data**
   - Scroll through the table
   - All columns are visible
   - Data loads automatically

3. **Search/Filter**
   - Type in "Search records" box (sidebar)
   - Searches across all visible columns
   - Results update immediately
   - Clear search box to see all records

### Selecting a Record to Edit

**IMPORTANT:** You must use the dropdown menu, not table clicks.

1. Look at the table to find your record
2. Scroll down to "Choose a record:" dropdown
3. Click the dropdown
4. Find your record in the list
5. Click to select

**Auto-Select:** If your search returns only 1 record, it will automatically be selected.

### Editing Records

Once a record is selected:

1. **Edit Form Appears**
   - Shows current values for all fields
   - Some fields are read-only (grayed out)
   - Others are editable

2. **Make Changes**
   - Click in editable fields
   - Enter new values
   - Required fields are marked
   - Validation happens in real-time

3. **Save Changes**
   - Click **"Update"** button at bottom
   - Wait for confirmation message
   - ✅ Green success message = saved
   - ❌ Red error message = not saved (check validation)

4. **Cancel Changes**
   - Click **"Cancel"** button
   - Form closes without saving
   - Selection is cleared

### Common Tasks

#### Task: Update Business Unit Coordinates

1. Select "Business Unit Details" table
2. Search for store code (e.g., "02")
3. Select from dropdown
4. Update Latitude and/or Longitude
5. Click "Update"
6. Verify success message

#### Task: Update Web Name Address

1. Select "Web Names" table
2. Search for business unit code
3. Select from dropdown
4. Update address fields
5. Click "Update"
6. Verify success message

#### Task: Change Store Hours

1. Select "Business Unit Details" table
2. Find and select your store
3. Update opening/closing times for specific days
4. Click "Update"
5. Confirm change saved

---

## Field Validation

### Business Unit Details

**Latitude**
- Must be between -90 and 90
- Decimal format (e.g., 43.1838)

**Longitude**
- Must be between -180 and 180
- Decimal format (e.g., -76.234)

**Dates**
- Use date picker
- Valid date format required

**Store Hours**
- Time format: HH:MM AM/PM
- Open time must be before close time

**Marketing Updatable**
- Checkbox (checked = True, unchecked = False)

### Web Names

**Display Name**
- Required field
- Cannot be empty

**Address Line 1**
- Required field
- Cannot be empty

**City**
- Required field
- Cannot be empty

**State**
- Required field
- Must be exactly 2 characters
- Automatically converted to uppercase

**Postal Code**
- Required field
- Cannot be empty

---

## Tips & Best Practices

### Search Tips
✅ Search is case-insensitive  
✅ Searches all visible columns  
✅ Partial matches work (e.g., "WM" finds "WM")  
✅ Clear search to see all records  
✅ One result? It auto-selects!  

### Selection Tips
✅ Use the dropdown, not table clicks  
✅ Look for record in table first  
✅ Then select from dropdown  
✅ Selected record shows below dropdown  
✅ Clear button resets everything  

### Editing Tips
✅ Check required fields (marked)  
✅ Watch for validation messages  
✅ Red messages = fix before saving  
✅ Green messages = successfully saved  
✅ Use Cancel if you change your mind  

### Safety
✅ Green "BACKUP MODE" = safe testing  
✅ All changes go to test tables  
✅ Production data is protected  
✅ Feel free to experiment!  

---

## Troubleshooting

### Problem: Can't see my record
**Solution:**
- Check if you're on the correct table
- Clear any search filters
- Click Refresh button
- Check if record exists in database

### Problem: Can't select a record
**Solution:**
- Use the dropdown below the table (not table clicks)
- Make sure you're clicking "Choose a record" dropdown
- If dropdown is empty, no records match current filters

### Problem: Update button doesn't work
**Solution:**
- Check for red validation error messages
- Fix any invalid fields
- Ensure all required fields are filled
- Try again after fixing errors

### Problem: Changes not saved
**Solution:**
- Look for error message
- Check you clicked "Update" not "Cancel"
- Verify you have permission to update
- Contact support if issue persists

### Problem: Search not working
**Solution:**
- Check spelling
- Try partial match instead of exact
- Clear search and try again
- Click Refresh to reload data

### Problem: App won't load
**Solution:**
- Check your internet connection
- Verify you're logged into Snowflake
- Try refreshing browser page
- Contact IT support if issue continues

---

## Important Notes

### Current Mode: BACKUP
🔒 The application is currently in **BACKUP MODE**

This means:
- All changes go to test tables only
- Production data is NOT affected
- Safe to make any updates
- Perfect for learning and testing

### When This Changes
When switched to **PRODUCTION MODE**:
- Changes will affect live data
- Be more careful with updates
- Double-check before clicking Update
- Contact admin if unsure

---

## Getting Help

### Quick References
- This guide: Full user instructions
- README.md: Technical overview
- CHANGELOG.md: Recent changes

### Support
1. Try troubleshooting section above
2. Check with your team administrator
3. Contact IT support with:
   - Screenshot of issue
   - What you were trying to do
   - Any error messages shown

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Focus search | Click search box |
| Clear search | Delete/Backspace in search box |
| Navigate dropdown | Arrow keys when dropdown open |
| Close form | Cancel button |
| Save changes | Update button |

---

## Frequently Asked Questions

**Q: Why can't I click rows in the table to select them?**  
A: The Snowflake version requires using the dropdown menu. This is a platform limitation.

**Q: How do I know if my changes were saved?**  
A: You'll see a green success message at the top. The data will also refresh showing your change.

**Q: Can I undo a change?**  
A: Currently, no automatic undo. You'll need to edit the record again and change it back manually.

**Q: Why are some fields grayed out?**  
A: Those are read-only fields that cannot be edited (like Store Code or Business Unit Code).

**Q: What happens if I search and get no results?**  
A: You'll see "No records found." Clear your search or try a different term.

**Q: Can I edit multiple records at once?**  
A: Currently, no. You must edit records one at a time.

**Q: Is there a limit to how many updates I can make?**  
A: No limit in BACKUP mode. Make as many updates as needed for testing.

**Q: How often does data refresh?**  
A: Automatically every 5 minutes, or click Refresh button for immediate update.

---

## Summary Checklist

New users should practice:

- [ ] Accessing the application in Snowsight
- [ ] Switching between tables
- [ ] Using the search function
- [ ] Selecting a record from dropdown
- [ ] Viewing the edit form
- [ ] Making a test change
- [ ] Clicking Update
- [ ] Verifying the success message
- [ ] Using the Clear button
- [ ] Using the Refresh button

Once comfortable, you're ready to use the application!

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-17  
**Environment:** BACKUP MODE (Safe Testing)

For technical documentation, see [README.md](../README.md)
