package com.example.animals;

/**
 * Base Animal class with common methods.
 */
public class Animal {

    private String name;
    private int age;

    public Animal(String name) {
        this.name = name;
        this.age = 0;
    }

    /**
     * Animal eats.
     */
    public void eat() {
        System.out.println(name + " is eating");
    }

    /**
     * Animal sleeps.
     */
    public void sleep() {
        System.out.println(name + " is sleeping");
    }

    /**
     * Get animal name.
     */
    public String getName() {
        return name;
    }

    /**
     * Make a sound - override in subclasses.
     */
    public void makeSound() {
        System.out.println(name + " makes a sound");
    }
}
