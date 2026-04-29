import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  type Expense,
  type Currency,
  type Traveler,
  CATEGORIES,
  TRAVELERS,
  generateId,
} from "@/lib/expenses"
import { Plus, Save, X, Check } from "lucide-react"
import { cn } from "@/lib/utils"

interface ExpenseFormProps {
  onSave: (expense: Expense) => void
  editingExpense: Expense | null
  onCancelEdit: () => void
}

export function ExpenseForm({ onSave, editingExpense, onCancelEdit }: ExpenseFormProps) {
  const [date, setDate] = useState("")
  const [description, setDescription] = useState("")
  const [category, setCategory] = useState<string>(CATEGORIES[0])
  const [currency, setCurrency] = useState<Currency>("HKD")
  const [amount, setAmount] = useState("")
  const [paidBy, setPaidBy] = useState<Traveler>(TRAVELERS[0])
  const [splitAmong, setSplitAmong] = useState<Traveler[]>([...TRAVELERS])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (editingExpense) {
      setDate(editingExpense.date)
      setDescription(editingExpense.description)
      setCategory(editingExpense.category)
      setCurrency(editingExpense.currency)
      setAmount(editingExpense.amount.toString())
      setPaidBy(editingExpense.paidBy)
      setSplitAmong(editingExpense.splitAmong)
      setIsOpen(true)
    }
  }, [editingExpense])

  const resetForm = () => {
    setDate("")
    setDescription("")
    setCategory(CATEGORIES[0])
    setCurrency("HKD")
    setAmount("")
    setPaidBy(TRAVELERS[0])
    setSplitAmong([...TRAVELERS])
  }

  const toggleSplit = (person: Traveler) => {
    setSplitAmong((prev) => {
      if (prev.includes(person)) {
        if (prev.length <= 1) return prev // at least one person
        return prev.filter((p) => p !== person)
      }
      return [...prev, person]
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!date || !description || !amount || parseFloat(amount) <= 0) return
    if (splitAmong.length === 0) return

    const expense: Expense = {
      id: editingExpense ? editingExpense.id : generateId(),
      date,
      description,
      category,
      currency,
      amount: parseFloat(amount),
      paidBy,
      splitAmong: [...splitAmong],
    }

    onSave(expense)
    resetForm()
    if (!editingExpense) setIsOpen(false)
    onCancelEdit()
  }

  const handleCancel = () => {
    resetForm()
    setIsOpen(false)
    onCancelEdit()
  }

  const inputClass = cn(
    "w-full h-10 px-3 rounded-md border border-input bg-card text-foreground",
    "text-sm transition-smooth",
    "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
    "placeholder:text-muted-foreground"
  )

  const labelClass = "block text-sm font-medium text-foreground mb-1.5"

  if (!isOpen && !editingExpense) {
    return (
      <Button onClick={() => setIsOpen(true)} className="w-full sm:w-auto">
        <Plus className="w-4 h-4 mr-2" />
        Add Expense
      </Button>
    )
  }

  return (
    <div className="bg-card border border-border rounded-lg p-6 shadow-sm animate-scale-in">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-foreground">
          {editingExpense ? "Edit Expense" : "Add New Expense"}
        </h3>
        <button
          onClick={handleCancel}
          className="w-8 h-8 rounded-full flex items-center justify-center text-muted-foreground hover:bg-accent hover:text-foreground transition-smooth"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Date */}
          <div>
            <label htmlFor="date" className={labelClass}>Date</label>
            <input
              id="date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className={inputClass}
              required
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className={labelClass}>Category</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className={inputClass}
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className={labelClass}>Description</label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., Sushi dinner in Shibuya"
            className={inputClass}
            required
          />
        </div>

        {/* Paid By */}
        <div>
          <label className={labelClass}>Paid By</label>
          <div className="flex gap-2">
            {TRAVELERS.map((person) => (
              <button
                key={person}
                type="button"
                onClick={() => setPaidBy(person)}
                className={cn(
                  "flex-1 h-10 rounded-md text-sm font-medium transition-smooth border",
                  paidBy === person
                    ? "gradient-primary text-primary-foreground border-transparent shadow-elegant"
                    : "bg-card text-foreground border-input hover:bg-accent"
                )}
              >
                {person}
              </button>
            ))}
          </div>
        </div>

        {/* Split Among */}
        <div>
          <label className={labelClass}>Split Among</label>
          <div className="flex gap-2">
            {TRAVELERS.map((person) => {
              const isSelected = splitAmong.includes(person)
              return (
                <button
                  key={person}
                  type="button"
                  onClick={() => toggleSplit(person)}
                  className={cn(
                    "flex-1 h-10 rounded-md text-sm font-medium transition-smooth border",
                    "flex items-center justify-center gap-1.5",
                    isSelected
                      ? "gradient-card-total text-primary-foreground border-transparent shadow-elegant"
                      : "bg-card text-foreground border-input hover:bg-accent"
                  )}
                >
                  {isSelected && <Check className="w-3.5 h-3.5" />}
                  {person}
                </button>
              )
            })}
          </div>
          <p className="text-xs text-muted-foreground mt-1.5">
            Each pays: {amount && parseFloat(amount) > 0
              ? currency === "HKD"
                ? `HK$ ${(parseFloat(amount) / splitAmong.length).toFixed(2)}`
                : `\u00a5 ${Math.round(parseFloat(amount) / splitAmong.length).toLocaleString()}`
              : "---"
            } per person
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Currency */}
          <div>
            <label className={labelClass}>Currency</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setCurrency("HKD")}
                className={cn(
                  "flex-1 h-10 rounded-md text-sm font-medium transition-smooth border",
                  currency === "HKD"
                    ? "gradient-card-hkd text-primary-foreground border-transparent shadow-elegant"
                    : "bg-card text-foreground border-input hover:bg-accent"
                )}
              >
                HK$ HKD
              </button>
              <button
                type="button"
                onClick={() => setCurrency("JPY")}
                className={cn(
                  "flex-1 h-10 rounded-md text-sm font-medium transition-smooth border",
                  currency === "JPY"
                    ? "gradient-card-jpy text-primary-foreground border-transparent shadow-elegant"
                    : "bg-card text-foreground border-input hover:bg-accent"
                )}
              >
                &yen; JPY
              </button>
            </div>
          </div>

          {/* Amount */}
          <div>
            <label htmlFor="amount" className={labelClass}>Amount</label>
            <input
              id="amount"
              type="number"
              step={currency === "HKD" ? "0.01" : "1"}
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder={currency === "HKD" ? "0.00" : "0"}
              className={inputClass}
              required
            />
          </div>
        </div>

        {/* Submit */}
        <div className="flex gap-3 pt-2">
          <Button type="submit" className="flex-1 sm:flex-none">
            {editingExpense ? (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            ) : (
              <>
                <Plus className="w-4 h-4 mr-2" />
                Add Expense
              </>
            )}
          </Button>
          <Button type="button" variant="outline" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
