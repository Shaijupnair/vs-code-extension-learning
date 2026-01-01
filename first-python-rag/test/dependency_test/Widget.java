package com.example.transactions;

/**
 * Widget class for testing dependencies.
 */
public class Widget {

    private int id;
    private String name;

    /**
     * Default constructor.
     */
    public Widget() {
        this.id = 0;
        this.name = "Default";
    }

    /**
     * Constructor with parameters.
     */
    public Widget(int id, String name) {
        this.id = id;
        this.name = name;
    }

    /**
     * Get widget ID.
     */
    public int getId() {
        return id;
    }

    /**
     * Get widget name.
     */
    public String getName() {
        return name;
    }
}
