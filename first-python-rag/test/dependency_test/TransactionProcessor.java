package com.example.transactions;

import java.util.List;

/**
 * Transaction processor with various dependencies.
 */
public class TransactionProcessor {

    private Widget widget;
    private List<Transaction> transactions;

    /**
     * Constructor with dependencies.
     */
    public TransactionProcessor(Widget widget) {
        this.widget = widget;
    }

    /**
     * Process a single transaction.
     * Dependencies: Transaction
     */
    public void processTransaction(Transaction t) {
        if (t.validate()) {
            System.out.println("Processing transaction: " + t.getId());
        }
    }

    /**
     * Process multiple transactions.
     * Dependencies: Transaction (in List, but should be extracted)
     */
    public int processBatch(List<Transaction> transactions) {
        int count = 0;
        for (Transaction t : transactions) {
            processTransaction(t);
            count++;
        }
        return count;
    }

    /**
     * Create a new transaction with widget.
     * Dependencies: Transaction, Widget
     */
    public Transaction createTransaction(String id, Widget w) {
        Transaction t = new Transaction(id, 100.0, "PURCHASE");
        System.out.println("Created by widget: " + w.getName());
        return t;
    }

    /**
     * Merge transactions.
     * Dependencies: Transaction (multiple parameters)
     */
    public Transaction mergeTransactions(Transaction t1, Transaction t2) {
        double totalAmount = t1.getAmount() + t2.getAmount();
        return new Transaction("MERGED", totalAmount, "MERGED");
    }

    /**
     * Process with primitives only - no dependencies.
     */
    public boolean validateAmount(double amount, int precision) {
        return amount > 0 && precision >= 0;
    }

    /**
     * Mixed parameters.
     * Dependencies: Widget (String is common type, ignored)
     */
    public Widget findWidget(String name, Widget defaultWidget) {
        if (name != null && !name.isEmpty()) {
            return new Widget(1, name);
        }
        return defaultWidget;
    }
}
