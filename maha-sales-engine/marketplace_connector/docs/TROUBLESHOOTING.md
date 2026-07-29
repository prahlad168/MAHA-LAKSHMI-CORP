# MAHA SALES ENGINE V1 - Troubleshooting

Common issues and solutions for marketplace connector.

## Publication Failures

### Problem: Product validation fails
**Solution:** Check package structure:
- `metadata.json` exists and is valid JSON
- `description.md` exists
- `pricing.json` exists and has valid price
- `thumbnail/` directory has image files
- `product/` directory has ZIP file

### Problem: Upload fails
**Solution:** Verify:
- File paths are correct
- Files are not locked by other processes
- Sufficient disk space
- Network connectivity to Gumroad

### Problem: Listing creation fails
**Solution:** Check:
- API key is valid
- Gumroad account is active
- Product limits not exceeded
- Required fields are populated

## Authentication Issues

### Problem: Connection test fails
**Solution:**
1. Verify API key is correct
2. Check API key has not expired
3. Ensure no IP restrictions on Gumroad account
4. Test with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" https://api.gumroad.com/api/v1/products
   ```

## Webhook Issues

### Problem: Webhooks not received
**Solution:**
1. Verify webhook URL is publicly accessible
2. Check firewall allows Gumroad IPs
3. Verify webhook secret matches
4. Check webhook logs in Gumroad dashboard

### Problem: Webhook signature verification fails
**Solution:**
1. Ensure webhook secret is identical on both sides
2. Check payload is not modified before verification
3. Use raw request body for signature calculation

## Performance Issues

### Problem: Slow publications
**Solution:**
1. Check file sizes - compress large files
2. Verify network bandwidth
3. Check database query performance
4. Enable caching

### Problem: Queue backlog
**Solution:**
1. Increase worker concurrency
2. Check for stuck publications
3. Review retry settings
4. Scale horizontally

## Database Issues

### Problem: Migration fails
**Solution:**
1. Check database permissions
2. Verify database is accessible
3. Review migration SQL for syntax errors
4. Check for existing tables/columns

### Problem: Connection pool exhausted
**Solution:**
1. Increase pool size
2. Check for connection leaks
3. Review long-running queries
4. Enable connection timeout
