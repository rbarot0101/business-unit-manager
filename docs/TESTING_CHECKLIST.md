# Business Unit Manager - Testing Checklist

## Pre-Testing Setup
- [x] Backup tables created (ZZZ_BUSINESS_UNIT_DETAILS_20260417, ZZZ_BUSINESS_UNIT_WEB_NAME_20260417)
- [x] Row counts verified (310 business units, 153 web names)
- [x] Application running in BACKUP mode
- [x] Connection to Snowflake established

## Phase 1: Application Structure ✅
- [x] App loads without errors
- [x] Page title displays correctly
- [x] Layout renders properly (header, sidebar, main area)
- [x] Session state initializes correctly
- [x] BACKUP mode indicator shows in header
- [x] Connection status displays

## Phase 2: Data Display ✅
### Business Unit Details Table
- [ ] Table loads with 310 records
- [ ] All columns display with proper formatting
- [ ] Latitude/Longitude show 6 decimal places
- [ ] Date columns formatted correctly
- [ ] Marketing Updatable shows as checkbox
- [ ] Search by Store Code filters results
- [ ] Row selection works (click on row)
- [ ] Selected row highlights properly
- [ ] Success message shows Store Code after selection

### Web Names Table
- [ ] Table loads with 153 records
- [ ] JOIN displays both STORE_CD and BUSINESS_UNIT_CD
- [ ] Display Name, Address fields show correctly
- [ ] Search by Display Name filters results
- [ ] Search by City filters results
- [ ] Search by Business Unit Code filters results
- [ ] Row selection works
- [ ] Success message shows Display Name and Business Unit CD

### General Data Display
- [ ] Record count displays correctly
- [ ] Empty search results show appropriate message
- [ ] Loading spinners appear during data fetch
- [ ] Cache works (subsequent loads faster)
- [ ] Refresh button clears cache and reloads data
- [ ] Clear Selection button deselects row

## Phase 3: Edit Forms ✅
### Business Unit Edit Form
- [ ] Form appears when row selected
- [ ] Store Code field is read-only
- [ ] All editable fields pre-filled with current data
- [ ] Latitude field accepts decimal numbers
- [ ] Longitude field accepts decimal numbers
- [ ] Open Date picker works
- [ ] Close Date picker works (allows null)
- [ ] Marketing Updatable checkbox reflects current state
- [ ] Store hours fields editable
- [ ] Update button present
- [ ] Cancel button present
- [ ] Cancel button closes form and clears selection

### Web Name Edit Form
- [ ] Form appears when row selected
- [ ] Store Code field is read-only
- [ ] Business Unit Code field is read-only
- [ ] Display Name field pre-filled
- [ ] Address Line 1 field pre-filled
- [ ] Address Line 2 field pre-filled (handles nulls)
- [ ] City, State, Postal Code pre-filled
- [ ] Required fields marked with asterisk
- [ ] Update button present
- [ ] Cancel button present
- [ ] Cancel button closes form and clears selection

## Phase 4: Update Operations ✅
### Business Unit Updates
- [ ] Latitude validation (must be -90 to 90)
- [ ] Longitude validation (must be -180 to 180)
- [ ] Invalid latitude shows error message
- [ ] Invalid longitude shows error message
- [ ] Valid update shows spinner
- [ ] Successful update shows success message
- [ ] Failed update shows error message
- [ ] Update clears cache
- [ ] Form closes after successful update
- [ ] Data refreshes to show updated values
- [ ] Verify update in database (query backup table)

### Web Name Updates
- [ ] Display Name required validation
- [ ] Address Line 1 required validation
- [ ] City required validation
- [ ] State required validation
- [ ] Postal Code required validation
- [ ] State must be 2 characters validation
- [ ] State auto-converts to uppercase
- [ ] Whitespace trimmed from all fields
- [ ] Empty required field shows error
- [ ] Valid update shows spinner
- [ ] Successful update shows success message
- [ ] Failed update shows error message
- [ ] Update clears cache
- [ ] Form closes after successful update
- [ ] Data refreshes to show updated values
- [ ] Verify update in database (query backup table)

## Phase 5: Polish & Testing ✅
### Connection Monitoring
- [ ] Connection status shows in header
- [ ] Server timestamp displays when connected
- [ ] Disconnected state shows error message
- [ ] Retry Connection button appears when disconnected
- [ ] Connection test caches for 1 minute

### Error Handling
- [ ] Database errors display user-friendly messages
- [ ] Network errors handled gracefully
- [ ] Invalid data handled without crashes
- [ ] Error boundary catches rendering errors
- [ ] Reload button appears on critical errors

### UI Polish
- [ ] Help section shows usage instructions
- [ ] Help shows current environment mode
- [ ] Help shows keyboard shortcuts
- [ ] Footer shows version number
- [ ] Footer shows environment (BACKUP/PRODUCTION)
- [ ] Footer shows database and user info
- [ ] Record counts display in header
- [ ] Last refresh timestamp updates correctly
- [ ] Refresh button clears all caches and selections
- [ ] Success message shows "Data refreshed!"

### Performance
- [ ] Initial load completes in <5 seconds
- [ ] Table selection responds immediately
- [ ] Form submission completes in <3 seconds
- [ ] Cache improves subsequent load times
- [ ] Large result sets don't cause lag

## Integration Testing
### Full Update Workflow - Business Unit
1. [ ] Navigate to Business Unit Details
2. [ ] Search for a specific store code
3. [ ] Select a row
4. [ ] Modify latitude/longitude
5. [ ] Modify dates
6. [ ] Toggle Marketing Updatable
7. [ ] Change store hours
8. [ ] Click Update
9. [ ] Verify success message
10. [ ] Verify form closes
11. [ ] Verify data refreshes
12. [ ] Re-search and verify changes persisted

### Full Update Workflow - Web Name
1. [ ] Navigate to Web Names
2. [ ] Search for a business unit
3. [ ] Select a row
4. [ ] Modify Display Name
5. [ ] Update address fields
6. [ ] Update city/state/postal code
7. [ ] Click Update
8. [ ] Verify success message
9. [ ] Verify form closes
10. [ ] Verify data refreshes
11. [ ] Re-search and verify changes persisted

### Edge Cases
- [ ] Test with empty search (shows all records)
- [ ] Test with search matching no records
- [ ] Test selecting different rows quickly
- [ ] Test clicking Update without changes
- [ ] Test maximum length inputs
- [ ] Test special characters in text fields
- [ ] Test null/empty date fields
- [ ] Test extreme lat/lon values (-90, 90, -180, 180)
- [ ] Test invalid lat/lon values (>90, <-90, >180, <-180)
- [ ] Test single character state codes (should fail)
- [ ] Test 3+ character state codes (should fail)
- [ ] Test navigation between tables with form open

## Environment Verification
- [ ] BACKUP mode indicator shows green "🔒 BACKUP MODE"
- [ ] Table names shown in info expander match ZZZ_*_20260417
- [ ] Help section confirms BACKUP mode
- [ ] Footer confirms BACKUP environment
- [ ] All updates go to backup tables (verified in database)
- [ ] Production tables remain untouched (row count unchanged)

## Go-Live Readiness (DO NOT EXECUTE YET)
- [ ] All above tests pass in BACKUP mode
- [ ] User approval received
- [ ] Production deployment plan reviewed
- [ ] Rollback plan documented
- [ ] Backup tables retention plan confirmed

## Post Go-Live Monitoring (AFTER switching to production)
- [ ] First production update successful
- [ ] No unintended side effects
- [ ] Data integrity maintained
- [ ] Error handling works in production
- [ ] Performance acceptable in production
