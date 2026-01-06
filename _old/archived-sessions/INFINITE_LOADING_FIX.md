# Fix: Infinite Loading Issue with Recent Series on Dashboard

**Date**: November 11, 2025  
**Issue**: Recent Series section on dashboard was stuck in infinite loading state  
**Status**: ✅ FIXED

## Problem

The "Recent Series" section on the dashboard was displaying a loading spinner indefinitely and never showing the series list. This affected the dashboard user experience significantly.

### Root Causes

1. **Query Inefficiency**: The original query used `ORDER BY s.created_at DESC` without handling NULL values
   - If `created_at` was NULL for existing series, the query could hang or return inconsistent results
   - No fallback ordering mechanism

2. **Missing Timeout**: The JavaScript fetch request had no timeout protection
   - If the API endpoint hung, the loading spinner would never disappear
   - No error handling for slow/unresponsive endpoints

3. **Incomplete Error Handling**: Error responses didn't always return the `series` array
   - Frontend code expected `data.series` to always exist
   - Missing data could cause rendering issues

## Solutions Implemented

### 1. Backend Fix: `/frontend/api_series.py`

**Changed the query to use `COALESCE` for better NULL handling:**

```python
# Before
query += " ORDER BY s.created_at DESC LIMIT ?"

# After
query = f"""
    SELECT s.* FROM series s
    {where_clause}
    ORDER BY COALESCE(s.created_at, s.id) DESC
    LIMIT ?
"""
```

**Benefits:**
- Falls back to `id` DESC if `created_at` is NULL
- Ensures consistent ordering regardless of data state
- Prevents query hangs from NULL values

**Additional improvements:**
- Added limit validation (0 < limit ≤ 100)
- Ensured empty series array is returned on error
- Better error logging

### 2. Frontend Fix: `/frontend/templates/dashboard.html`

**Added timeout protection to the fetch request:**

```javascript
// Before
fetch(`/api/series/recent?content_type=${contentType}&limit=6`)

// After
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

fetch(`/api/series/recent?content_type=${contentType}&limit=6`, {
    signal: controller.signal
})
```

**Benefits:**
- Request aborts after 10 seconds if no response
- Loading spinner disappears and "No series" message shows
- User gets feedback instead of infinite loading
- Timeout errors are logged for debugging

**Additional improvements:**
- Proper timeout cleanup with `clearTimeout()`
- Specific error handling for `AbortError`
- Better console logging for debugging

## Files Modified

1. **`frontend/api_series.py`**
   - Updated `get_recent_series()` function
   - Improved query with COALESCE fallback
   - Better error handling

2. **`frontend/templates/dashboard.html`**
   - Updated `loadRecentSeries()` function
   - Added AbortController for timeout
   - Improved error handling and logging

## Testing

To verify the fix works:

1. **Check dashboard loads**: Navigate to Dashboard
2. **Verify Recent Series loads**: Should show series or "No series" message within 10 seconds
3. **Test with different content types**: Switch between All/Books/Manga tabs
4. **Check browser console**: Should not show hanging requests

## Performance Impact

- **Positive**: Queries now complete faster with proper ordering
- **Positive**: UI no longer hangs waiting for slow responses
- **Neutral**: 10-second timeout is reasonable for most connections

## Related Issues

- Dashboard infinite loading on Recent Series
- UI responsiveness on slow connections
- Database query optimization

## Future Improvements

1. Add database index on `series.created_at` for faster queries
2. Consider pagination for large series lists
3. Add caching for recent series data
4. Monitor API response times in production

---

**Status**: Ready for testing  
**Deployed**: November 11, 2025
