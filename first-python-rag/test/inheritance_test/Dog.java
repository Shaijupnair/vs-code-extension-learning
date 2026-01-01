package com.example.animals;

/**
 * Dog class that extends Animal.
 */
public class Dog extends Animal {

    private String breed;

    public Dog(String name, String breed) {
        super(name);
        this.breed = breed;
    }

    /**
     * Dog barks.
     */
    public void bark() {
        System.out.println(getName() + " barks: Woof!");
    }

    /**
     * Dog wags tail.
     */
    public void wagTail() {
        System.out.println(getName() + " is wagging tail");
    }

    /**
     * Override makeSound from Animal.
     */
    @Override
    public void makeSound() {
        bark();
    }

    /**
     * Get breed.
     */
    public String getBreed() {
        return breed;
    }
}
