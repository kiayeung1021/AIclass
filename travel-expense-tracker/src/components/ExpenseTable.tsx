import { useState } from "react"
import { type Expense, formatCurrency } from "@/lib/expenses"
import { Button } from "@/components/ui/button"
import { Pencil, Trash2, ChevronDown, ChevronUp, Search } from "lucide-react"
import { cn } from "@/lib/utils"

interface ExpenseTableProps {
  expenses: Expense[]
  onEdit: (expense: Expense) => void
  onDelete: (id: string) => void
}

type SortField = "date" | "amount" | "category" | "currency" | "paidBy"
type SortDir = "asc" | "desc"

export function ExpenseTable({ expenses, onEdit, onDelete }: ExpenseTableProps) {
  const [sortField, setSortField] = useState<SortField>("date")
  const [sortDir, setSortDir] = useState<SortDir>("desc")
  const [filterCurrency, setFilterCurrency] = useState<"ALL" | "HKD" | "JPY">("ALL")
  const [searchQuery, setSearchQuery] = useState("")
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDir("desc")
    }
  }

  const filtered = expenses
    .filter((e) => filterCurrency === "ALL" || e.currency === filterCurrency)
    .filter(
      (e) =>
        searchQuery === "" ||
        e.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        e.paidBy.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1
      if (sortField === "date") return dir * a.date.localeCompare(b.date)
      if (sortField === "amount") return dir * (a.amount - b.amount)
      if (sortField === "category") return dir * a.category.localeCompare(b.category)
      if (sortField === "currency") return dir * a.currency.localeCompare(b.currency)
      if (sortField === "paidBy") return dir * a.paidBy.localeCompare(b.paidBy)
      return 0
    })

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null
    return sortDir === "asc" ? (
      <ChevronUp className="w-3.5 h-3.5 inline ml-1" />
    ) : (
      <ChevronDown className="w-3.5 h-3.5 inline ml-1" />
    )
  }

  const thClass = cn(
    "px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider",
    "text-muted-foreground cursor-pointer hover:text-foreground transition-smooth select-none"
  )

  const handleDeleteClick = (id: string) => {
    if (deleteConfirm === id) {
      onDelete(id)
      setDeleteConfirm(null)
    } else {
      setDeleteConfirm(id)
      setTimeout(() => setDeleteConfirm(null), 3000)
    }
  }

  return (
    <div className="bg-card border border-border rounded-lg shadow-sm overflow-hidden">
      {/* Filters */}
      <div className="p-4 border-b border-border flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search expenses or names..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={cn(
              "w-full h-9 pl-9 pr-3 rounded-md border border-input bg-background text-foreground",
              "text-sm transition-smooth",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "placeholder:text-muted-foreground"
            )}
          />
        </div>
        <div className="flex gap-1.5">
          {(["ALL", "HKD", "JPY"] as const).map((cur) => (
            <button
              key={cur}
              onClick={() => setFilterCurrency(cur)}
              className={cn(
                "px-3 h-9 rounded-md text-xs font-medium transition-smooth border",
                filterCurrency === cur
                  ? "gradient-primary text-primary-foreground border-transparent"
                  : "bg-background text-foreground border-input hover:bg-accent"
              )}
            >
              {cur}
            </button>
          ))}
        </div>
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className={thClass} onClick={() => handleSort("date")}>
                Date <SortIcon field="date" />
              </th>
              <th className={cn(thClass, "cursor-default hover:text-muted-foreground")}>
                Description
              </th>
              <th className={thClass} onClick={() => handleSort("paidBy")}>
                Paid By <SortIcon field="paidBy" />
              </th>
              <th className={cn(thClass, "cursor-default hover:text-muted-foreground")}>
                Split
              </th>
              <th className={thClass} onClick={() => handleSort("currency")}>
                Currency <SortIcon field="currency" />
              </th>
              <th className={thClass} onClick={() => handleSort("amount")}>
                Amount <SortIcon field="amount" />
              </th>
              <th className={cn(thClass, "text-right cursor-default hover:text-muted-foreground")}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-muted-foreground text-sm">
                  {expenses.length === 0
                    ? "No expenses yet. Add your first expense above!"
                    : "No matching expenses found."}
                </td>
              </tr>
            ) : (
              filtered.map((expense, i) => (
                <tr
                  key={expense.id}
                  className={cn(
                    "border-b border-border/50 transition-smooth hover:bg-accent/30",
                    "animate-fade-in"
                  )}
                  style={{ animationDelay: `${i * 0.03}s` }}
                >
                  <td className="px-4 py-3 text-sm text-foreground whitespace-nowrap">
                    {expense.date}
                  </td>
                  <td className="px-4 py-3 text-sm text-foreground max-w-[180px] truncate">
                    {expense.description}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full gradient-primary text-primary-foreground">
                      {expense.paidBy}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1 flex-wrap">
                      {expense.splitAmong.map((person) => (
                        <span
                          key={person}
                          className="text-xs font-medium px-2 py-0.5 rounded-full bg-accent text-accent-foreground"
                        >
                          {person}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "text-xs font-bold px-2 py-1 rounded",
                        expense.currency === "HKD"
                          ? "gradient-card-hkd text-primary-foreground"
                          : "gradient-card-jpy text-primary-foreground"
                      )}
                    >
                      {expense.currency}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm font-semibold text-foreground whitespace-nowrap">
                    {formatCurrency(expense.amount, expense.currency)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => onEdit(expense)}
                        title="Edit"
                      >
                        <Pencil className="w-4 h-4 text-primary" />
                      </Button>
                      <Button
                        variant={deleteConfirm === expense.id ? "destructive" : "ghost"}
                        size="icon"
                        onClick={() => handleDeleteClick(expense.id)}
                        title={deleteConfirm === expense.id ? "Click again to confirm" : "Delete"}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden divide-y divide-border">
        {filtered.length === 0 ? (
          <div className="px-4 py-12 text-center text-muted-foreground text-sm">
            {expenses.length === 0
              ? "No expenses yet. Add your first expense above!"
              : "No matching expenses found."}
          </div>
        ) : (
          filtered.map((expense) => (
            <div key={expense.id} className="p-4 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-foreground">{expense.description}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{expense.date}</p>
                </div>
                <span
                  className={cn(
                    "text-xs font-bold px-2 py-1 rounded",
                    expense.currency === "HKD"
                      ? "gradient-card-hkd text-primary-foreground"
                      : "gradient-card-jpy text-primary-foreground"
                  )}
                >
                  {expense.currency}
                </span>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full gradient-primary text-primary-foreground">
                  {expense.paidBy}
                </span>
                <span className="text-xs text-muted-foreground">for</span>
                {expense.splitAmong.map((person) => (
                  <span
                    key={person}
                    className="text-xs font-medium px-2 py-0.5 rounded-full bg-accent text-accent-foreground"
                  >
                    {person}
                  </span>
                ))}
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">
                  {formatCurrency(expense.amount, expense.currency)}
                </span>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => onEdit(expense)}>
                    <Pencil className="w-4 h-4 text-primary" />
                  </Button>
                  <Button
                    variant={deleteConfirm === expense.id ? "destructive" : "ghost"}
                    size="icon"
                    onClick={() => handleDeleteClick(expense.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
