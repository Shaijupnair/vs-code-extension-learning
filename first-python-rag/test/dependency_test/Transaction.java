package com.example.transactions;

/**
 * Transaction class with various constructors.
 */
public class Transaction {

    private String id;
    private double amount;
    private String type;

    /**
     * Default constructor.
     */
    public Transaction() {
        this.id = "";
        this.amount = 0.0;
        this.type = "UNKNOWN";
    }

    /**
     * Constructor with ID only.
     */
    public Transaction(String id) {
        this.id = id;
        this.amount = 0.0;
        this.type = "UNKNOWN";
    }

    /**
     * Full constructor.
     */
    public Transaction(String id, double amount, String type) {
        this.id = id;
        this.amount = amount;
        this.type = type;
    }

    /**
     * Get transaction ID.
     */
    public String getId() {
        return id;
    }

    /**
     * Get amount.
     */
    public double getAmount() {
        return amount;
    }

    /**
     * Validate transaction.
     */
    public boolean validate() {
        return amount > 0 && id != null && !id.isEmpty();
    }
}
