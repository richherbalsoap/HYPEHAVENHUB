# Project Rules — HYPEHAVENHUB

## Static Files Deployment Rule

**CRITICAL**: This Django project uses WhiteNoise to serve static files from the `staticfiles/` directory (NOT from `static/`).

Whenever you edit ANY file inside `static/` (CSS, JS, images, etc.), you **MUST** run the following command **before** committing and deploying:

```bash
python manage.py collectstatic --noinput
```

Then **include the updated `staticfiles/` files in the git commit** alongside the source `static/` changes.

### Why?
- `static/` = source files (where you edit)
- `staticfiles/` = compiled output (what Vercel/WhiteNoise actually serves to users)
- If you skip `collectstatic`, the live site will keep serving the OLD files

### Correct workflow:
1. Edit files in `static/css/` or `static/js/`
2. Run `python manage.py collectstatic --noinput`
3. `git add static/ staticfiles/`
4. `git commit` and `git push`
5. Run `./deploy.bat`

## Automatic GitHub & Vercel Deployment Rule

**CRITICAL**: Whenever ANY code update or bug fix is completed, you MUST automatically perform deployment to both GitHub and Vercel:
1. Run `python manage.py collectstatic --noinput` (if any static files were touched).
2. Commit all updated code: `git add .` and `git commit -m "<descriptive message>"`.
3. Push to GitHub repository: `git push origin main`.
4. Deploy live to Vercel: run `./deploy.bat` (or `npx vercel@latest --prod --yes`).

## Vercel CLI Scope Rule

**CRITICAL**: Always use `npx vercel@latest --prod --yes` in `./deploy.bat` to ensure Vercel deploys directly to the team project (`hypehavenhub/hypehavenhub`) and aliases automatically to `https://hypehavenhub.in`. Never use outdated local CLI commands without `@latest`.
## Permanent Shiprocket Integration Rule

**CRITICAL**: The Shiprocket integration MUST NEVER be altered or reverted from these locked settings:

1. **Primary Channel Priority**: `SHIPROCKET_CHANNEL_ID` (`8087473` - `HYPEHAVENHUB (CUSTOM)`) MUST ALWAYS take priority over secondary channel IDs. Never override or prioritize secondary channels over `8087473`.
2. **API Credentials**: `SHIPROCKET_EMAIL` (`api@hypehavenhub.in`) and `SHIPROCKET_PICKUP_LOCATION` (`abhi`) MUST be preserved as defaults in `settings.py` and `.env`.
3. **State Normalization**: Indian state codes (e.g. `GJ`, `MH`, `KA`) MUST ALWAYS be normalized to full names (`Gujarat`, `Maharashtra`, `Karnataka`) in `store/shipping.py` using `normalize_indian_state` before dispatching to Shiprocket API.
4. **Address Parsing**: Razorpay Magic Checkout address parsing MUST check all key variations (`line1`, `address1`, `street_address`, `city`, `district`, `state_code`, `zipcode`, `pincode`) and ALWAYS create complete `Address` objects.
5. **Customer Experience**: Paid customer orders MUST ALWAYS maintain status `confirmed` and NEVER display error banners or warning alerts on the order confirmation page. Any sync errors must be logged silently for admin retry only.
