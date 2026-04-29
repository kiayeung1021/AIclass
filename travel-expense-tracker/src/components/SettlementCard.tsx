import {
  type Expense,
  type Currency,
  type Traveler,
  TRAVELERS,
  formatCurrency,
  calculateBalances,
  calculateSettlements,
} from "@/lib/expenses"
import { cn } from "@/lib/utils"
import { ArrowRight, Users, DollarSign } from "lucide-react"

interface SettlementCardProps {
  expenses: Expense[]
}

export function SettlementCard({ expenses }: SettlementCardProps) {
  const balances = calculateBalances(expenses)
  const settlements = calculateSettlements(expenses)

  const hasAnyExpense = expenses.length > 0

  return (
    <div className="space-y-4">
      {/* Per-person spent & balance breakdown */}
      <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border flex items-center gap-2">
          <Users className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">Per-Person Balance</h3>
        </div>

        {!hasAnyExpense ? (
          <div className="p-6 text-center text-sm text-muted-foreground">
            Add expenses to see each person's balance.
          </div>
        ) : (
          <div className="divide-y divide-border">
            {TRAVELERS.map((person) => (
              <PersonRow
                key={person}
                person={person}
                expenses={expenses}
                balances={balances}
              />
            ))}
          </div>
        )}
      </div>

      {/* Settlements */}
      <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
        <div className="p-4 border-b border-border flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">Settlements</h3>
          <span className="text-xs text-muted-foreground ml-auto">Who pays whom</span>
        </div>

        {settlements.length === 0 ? (
          <div className="p-6 text-center text-sm text-muted-foreground">
            {hasAnyExpense ? "All settled! No payments needed." : "Add expenses to calculate settlements."}
          </div>
        ) : (
          <div className="divide-y divide-border">
            {settlements.map((s, i) => (
              <div
                key={`${s.from}-${s.to}-${s.currency}-${i}`}
                className="p-4 flex items-center gap-3 animate-fade-in"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <span className="text-sm font-semibold text-foreground min-w-[60px]">
                  {s.from}
                </span>
                <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0" />
                <span className="text-sm font-semibold text-foreground min-w-[60px]">
                  {s.to}
                </span>
                <span className="ml-auto flex items-center gap-2">
                  <span
                    className={cn(
                      "text-xs font-bold px-2 py-0.5 rounded",
                      s.currency === "HKD"
                        ? "gradient-card-hkd text-primary-foreground"
                        : "gradient-card-jpy text-primary-foreground"
                    )}
                  >
                    {s.currency}
                  </span>
                  <span className="text-sm font-bold text-foreground">
                    {formatCurrency(s.amount, s.currency)}
                  </span>
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function PersonRow({
  person,
  expenses,
  balances,
}: {
  person: Traveler
  expenses: Expense[]
  balances: Record<Currency, Record<Traveler, number>>
}) {
  const paidHKD = expenses
    .filter((e) => e.paidBy === person && e.currency === "HKD")
    .reduce((s, e) => s + e.amount, 0)
  const paidJPY = expenses
    .filter((e) => e.paidBy === person && e.currency === "JPY")
    .reduce((s, e) => s + e.amount, 0)

  const balHKD = balances.HKD[person]
  const balJPY = balances.JPY[person]

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-foreground">{person}</span>
        <div className="flex gap-3">
          {Math.abs(balHKD) > 0.005 && (
            <span
              className={cn(
                "text-xs font-bold px-2 py-1 rounded",
                balHKD > 0
                  ? "bg-success/10 text-success"
                  : "bg-destructive/10 text-destructive"
              )}
            >
              {balHKD > 0 ? "+" : ""}{formatCurrency(balHKD, "HKD")}
            </span>
          )}
          {Math.abs(balJPY) > 0.005 && (
            <span
              className={cn(
                "text-xs font-bold px-2 py-1 rounded",
                balJPY > 0
                  ? "bg-success/10 text-success"
                  : "bg-destructive/10 text-destructive"
              )}
            >
              {balJPY > 0 ? "+" : ""}{formatCurrency(balJPY, "JPY")}
            </span>
          )}
          {Math.abs(balHKD) <= 0.005 && Math.abs(balJPY) <= 0.005 && (
            <span className="text-xs font-medium text-muted-foreground px-2 py-1">
              Settled
            </span>
          )}
        </div>
      </div>
      <div className="flex gap-4 text-xs text-muted-foreground">
        {paidHKD > 0 && <span>Paid {formatCurrency(paidHKD, "HKD")}</span>}
        {paidJPY > 0 && <span>Paid {formatCurrency(paidJPY, "JPY")}</span>}
        {paidHKD === 0 && paidJPY === 0 && <span>No payments yet</span>}
      </div>
    </div>
  )
}
