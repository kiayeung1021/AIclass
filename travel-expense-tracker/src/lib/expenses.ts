export const TRAVELERS = ["Stanley", "Ash", "Kia"] as const
export type Traveler = (typeof TRAVELERS)[number]

export interface Expense {
  id: string
  date: string
  description: string
  category: string
  currency: "HKD" | "JPY"
  amount: number
  paidBy: Traveler
  splitAmong: Traveler[]
}

export type Currency = "HKD" | "JPY"

// Google Apps Script Web App URL
const GAS_API_URL = "https://script.google.com/macros/s/AKfycbwQPTMaVgnVwJO4QQhrcQ-pdKDBryTsckvkLxK30UOaDDQB0RWdHZv4Xl21c3CRPsda/exec"

export const CATEGORIES = [
  "Food & Dining",
  "Transport",
  "Accommodation",
  "Shopping",
  "Entertainment",
  "Sightseeing",
  "Others",
] as const

/** Calculate per-person balances: positive = is owed money, negative = owes money */
export function calculateBalances(expenses: Expense[]) {
  const balances: Record<Currency, Record<Traveler, number>> = {
    HKD: { Stanley: 0, Ash: 0, Kia: 0 },
    JPY: { Stanley: 0, Ash: 0, Kia: 0 },
  }

  for (const exp of expenses) {
    const share = exp.amount / exp.splitAmong.length
    // Payer gets credit for the full amount
    balances[exp.currency][exp.paidBy] += exp.amount
    // Each person in splitAmong is debited their share
    for (const person of exp.splitAmong) {
      balances[exp.currency][person] -= share
    }
  }

  return balances
}

export interface Settlement {
  from: Traveler
  to: Traveler
  amount: number
  currency: Currency
}

/** Calculate simplified settlements to settle all debts */
export function calculateSettlements(expenses: Expense[]): Settlement[] {
  const balances = calculateBalances(expenses)
  const settlements: Settlement[] = []

  for (const currency of ["HKD", "JPY"] as Currency[]) {
    const bal = { ...balances[currency] }
    const debtors = TRAVELERS.filter((t) => bal[t] < -0.005).map((t) => ({ name: t, amount: bal[t] }))
    const creditors = TRAVELERS.filter((t) => bal[t] > 0.005).map((t) => ({ name: t, amount: bal[t] }))

    debtors.sort((a, b) => a.amount - b.amount) // most negative first
    creditors.sort((a, b) => b.amount - a.amount) // most positive first

    let i = 0
    let j = 0
    while (i < debtors.length && j < creditors.length) {
      const owed = creditors[j].amount
      const debt = -debtors[i].amount
      const transfer = Math.min(owed, debt)

      if (transfer > 0.005) {
        settlements.push({
          from: debtors[i].name,
          to: creditors[j].name,
          amount: Math.round(transfer * 100) / 100,
          currency,
        })
      }

      creditors[j].amount -= transfer
      debtors[i].amount += transfer

      if (Math.abs(debtors[i].amount) < 0.005) i++
      if (Math.abs(creditors[j].amount) < 0.005) j++
    }
  }

  return settlements
}

export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 9)
}

export function formatCurrency(amount: number, currency: Currency): string {
  if (currency === "HKD") {
    return `HK$ ${amount.toLocaleString("en-HK", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
  return `\u00a5 ${amount.toLocaleString("ja-JP", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

// Helper function to handle GAS requests with proper CORS
async function gasRequest(url: string, options?: RequestInit): Promise<any> {
  const response = await fetch(url, {
    ...options,
    mode: 'cors',
    credentials: 'omit',
  })
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }
  
  return response.json()
}

// API Functions for Google Apps Script
export async function fetchExpenses(): Promise<Expense[]> {
  const result = await gasRequest(`${GAS_API_URL}?action=get`)
  if (result.success) {
    return result.data
  }
  throw new Error(result.error || 'Failed to fetch expenses')
}

export async function addExpenseAPI(expense: Expense): Promise<string> {
  const result = await gasRequest(GAS_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'add', expense })
  })
  if (result.success) {
    return result.id
  }
  throw new Error(result.error || 'Failed to add expense')
}

export async function updateExpenseAPI(expense: Expense): Promise<void> {
  const result = await gasRequest(GAS_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'update', expense })
  })
  if (!result.success) {
    throw new Error(result.error || 'Failed to update expense')
  }
}

export async function deleteExpenseAPI(id: string): Promise<void> {
  const result = await gasRequest(GAS_API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'delete', id })
  })
  if (!result.success) {
    throw new Error(result.error || 'Failed to delete expense')
  }
}


