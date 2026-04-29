import { useState, useCallback, useEffect } from "react"
import { type Expense, fetchExpenses, addExpenseAPI, updateExpenseAPI, deleteExpenseAPI } from "@/lib/expenses"
import { BalanceCards } from "@/components/BalanceCards"
import { ExpenseForm } from "@/components/ExpenseForm"
import { ExpenseTable } from "@/components/ExpenseTable"
import { SettlementCard } from "@/components/SettlementCard"
import { ToastContainer, showToast } from "@/components/Toast"
import { Plane } from "lucide-react"

function App() {
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load expenses from API on mount
  useEffect(() => {
    fetchExpenses().then((data) => {
      setExpenses(data)
      setIsLoading(false)
    })
  }, [])

  const updateExpenses = useCallback((updater: (prev: Expense[]) => Expense[]) => {
    setExpenses((prev) => updater(prev))
  }, [])

  const handleSave = useCallback(
    async (expense: Expense) => {
      const exists = expenses.find((e) => e.id === expense.id)
      try {
        if (exists) {
          await updateExpenseAPI(expense)
          updateExpenses((prev) => prev.map((e) => (e.id === expense.id ? expense : e)))
          showToast("Expense updated successfully")
        } else {
          const newId = await addExpenseAPI(expense)
          expense.id = newId
          updateExpenses((prev) => [expense, ...prev])
          showToast("Expense added successfully")
        }
        setEditingExpense(null)
      } catch (error) {
        showToast("Failed to save expense. Please try again.")
        console.error(error)
      }
    },
    [expenses, updateExpenses]
  )

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteExpenseAPI(id)
        updateExpenses((prev) => prev.filter((e) => e.id !== id))
        showToast("Expense deleted")
      } catch (error) {
        showToast("Failed to delete expense. Please try again.")
        console.error(error)
      }
    },
    [updateExpenses]
  )

  const handleEdit = useCallback((expense: Expense) => {
    setEditingExpense(expense)
    window.scrollTo({ top: 0, behavior: "smooth" })
  }, [])

  const handleCancelEdit = useCallback(() => {
    setEditingExpense(null)
  }, [])

  return (
    <div className="min-h-screen gradient-subtle">
      <ToastContainer />

      {/* Header */}
      <header className="relative overflow-hidden">
        <div
          className="gradient-hero"
          style={{
            minHeight: "220px",
            position: "relative",
          }}
        >
          {/* Hero background image overlay */}
          <div
            className="absolute inset-0 opacity-15 bg-cover bg-center"
            style={{ backgroundImage: "url('/images/travel-hero.png')" }}
          />
          <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-primary-foreground/20 flex items-center justify-center">
                <Plane className="w-5 h-5 text-primary-foreground" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-primary-foreground tracking-tight">
                Travel Expense Tracker
              </h1>
            </div>
            <p className="text-primary-foreground/80 text-sm sm:text-base max-w-lg">
              Track your Japan trip spending in HKD and JPY. Split expenses between Stanley, Ash, and Kia.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 -mt-6 pb-16 space-y-6">
        {isLoading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-muted-foreground">Loading expenses...</p>
          </div>
        )}

        {/* Balance Cards */}
        <section>
          <BalanceCards expenses={expenses} />
        </section>

        {/* Add / Edit Form */}
        <section>
          <ExpenseForm
            onSave={handleSave}
            editingExpense={editingExpense}
            onCancelEdit={handleCancelEdit}
          />
        </section>

        {/* Expense Table */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-3">Expense Records</h2>
          <ExpenseTable
            expenses={expenses}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </section>

        {/* Settlement */}
        <section>
          <h2 className="text-lg font-semibold text-foreground mb-3">Balance & Settlements</h2>
          <SettlementCard expenses={expenses} />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6">
        <p className="text-center text-xs text-muted-foreground">
          Travel Expense Tracker &mdash; Data is synced to Google Sheets.
        </p>
      </footer>
    </div>
  )
}

export default App
