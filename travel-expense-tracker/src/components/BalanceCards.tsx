import { cn } from "@/lib/utils"
import { type Expense, formatCurrency } from "@/lib/expenses"
import { DollarSign, TrendingUp } from "lucide-react"

interface BalanceCardsProps {
  expenses: Expense[]
}

export function BalanceCards({ expenses }: BalanceCardsProps) {
  const hkdTotal = expenses
    .filter((e) => e.currency === "HKD")
    .reduce((sum, e) => sum + e.amount, 0)

  const jpyTotal = expenses
    .filter((e) => e.currency === "JPY")
    .reduce((sum, e) => sum + e.amount, 0)

  const hkdCount = expenses.filter((e) => e.currency === "HKD").length
  const jpyCount = expenses.filter((e) => e.currency === "JPY").length

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
      {/* HKD Card */}
      <div
        className={cn(
          "gradient-card-hkd rounded-lg p-6 text-primary-foreground",
          "shadow-elegant animate-fade-in"
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-foreground/20 flex items-center justify-center">
              <DollarSign className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium opacity-90">HKD Balance</span>
          </div>
          <span className="text-xs opacity-70">{hkdCount} records</span>
        </div>
        <p className="text-3xl font-bold tracking-tight">
          {formatCurrency(hkdTotal, "HKD")}
        </p>
        <p className="text-xs mt-2 opacity-70">Hong Kong Dollar</p>
      </div>

      {/* JPY Card */}
      <div
        className={cn(
          "gradient-card-jpy rounded-lg p-6 text-primary-foreground",
          "shadow-elegant animate-fade-in"
        )}
        style={{ animationDelay: "0.1s" }}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-foreground/20 flex items-center justify-center">
              <span className="text-sm font-bold">&yen;</span>
            </div>
            <span className="text-sm font-medium opacity-90">JPY Balance</span>
          </div>
          <span className="text-xs opacity-70">{jpyCount} records</span>
        </div>
        <p className="text-3xl font-bold tracking-tight">
          {formatCurrency(jpyTotal, "JPY")}
        </p>
        <p className="text-xs mt-2 opacity-70">Japanese Yen</p>
      </div>

      {/* Total Records Card */}
      <div
        className={cn(
          "gradient-card-total rounded-lg p-6 text-primary-foreground",
          "shadow-elegant animate-fade-in sm:col-span-2 lg:col-span-1"
        )}
        style={{ animationDelay: "0.2s" }}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-foreground/20 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium opacity-90">Total Records</span>
          </div>
        </div>
        <p className="text-3xl font-bold tracking-tight">{expenses.length}</p>
        <p className="text-xs mt-2 opacity-70">
          {hkdCount} HKD + {jpyCount} JPY entries
        </p>
      </div>
    </div>
  )
}
