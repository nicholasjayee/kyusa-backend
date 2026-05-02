1. **Client books a service** → booking status `pending`.
2. **Provider accepts** → booking status `accepted`.
3. **Provider delivers the service** → provider calls `POST /provider/bookings/{id}/complete`.
4. **System does:**
   - Calculates commission based on `CommissionRule` (department or global).
   - Updates booking status to `completed`, sets `completed_at`.
   - Creates a `ProviderEarnings` record with:
     - `total_amount` = booking total price
     - `commission_amount` = calculated commission
     - `net_amount` = total - commission
     - `status` = `pending` (not yet available for payout)
5. **Why `pending`?**  
   To allow a dispute window or a confirmation step (e.g., client confirms satisfaction). In many marketplaces, earnings become `available` after a certain period (e.g., 7 days) or after client's explicit confirmation.
6. **When earnings become `available`** (not yet automated in our code – you can manually change via admin or implement a background job), the provider can request a payout.
7. **Provider requests payout** → `POST /api/provider/payouts` with amount and destination.
   - System checks available balance (sum of earnings with `status='available'`).
   - Creates a `Payout` record with `status='requested'`.
   - (Future) Admin processes the payout and marks it as `completed`.

So the earnings originate from the **total_amount** of each completed booking, minus commission. Currently, the `pending` status requires manual or automatic release before payout can be requested.
