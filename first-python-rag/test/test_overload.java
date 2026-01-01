package com.example.test;

/**
 * Test class for method overloading verification.
 * Contains multiple overloaded methods to test parser handling.
 */
public class OverloadTest {
    
    private int counter;
    private String name;
    
    /**
     * Test method with no parameters.
     */
    public void test() {
        System.out.println("Test with no parameters");
        counter++;
    }
    
    /**
     * Test method with int parameter.
     */
    public void test(int value) {
        System.out.println("Test with int: " + value);
        counter = value;
    }
    
    /**
     * Test method with String parameter.
     */
    public void test(String message) {
        System.out.println("Test with String: " + message);
        name = message;
    }
    
    /**
     * Test method with multiple parameters.
     */
    public void test(int value, String message) {
        System.out.println("Test with int and String: " + value + ", " + message);
        counter = value;
        name = message;
    }
    
    /**
     * Calculate method with int parameters.
     */
    public int calculate(int x) {
        return x * 2;
    }
    
    /**
     * Calculate method with String parameter - returns length.
     */
    public int calculate(String x) {
        return x.length();
    }
    
    /**
     * Calculate with two int parameters.
     */
    public int calculate(int base, int index) {
        return base + index;
    }
    
    /**
     * Calculate with mixed types.
     */
    public double calculate(int base, double multiplier) {
        return base * multiplier;
    }
    
    /**
     * Process method with different return types (overload by parameters).
     */
    public String process(int value) {
        return "Processed: " + value;
    }
    
    /**
     * Process method returning boolean.
     */
    public boolean process(String input, boolean validate) {
        return validate && input != null && !input.isEmpty();
    }
}
