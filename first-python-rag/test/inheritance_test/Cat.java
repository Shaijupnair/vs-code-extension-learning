package com.example.animals;

/**
 * Cat class that extends Animal.
 */
public class Cat extends Animal {

    private boolean indoor;

    public Cat(String name, boolean indoor) {
        super(name);
        this.indoor = indoor;
    }

    /**
     * Cat meows.
     */
    public void meow() {
        System.out.println(getName() + " meows: Meow!");
    }

    /**
     * Cat purrs.
     */
    public void purr() {
        System.out.println(getName() + " purrs");
    }

    /**
     * Override makeSound from Animal.
     */
    @Override
    public void makeSound() {
        meow();
    }

    /**
     * Check if indoor cat.
     */
    public boolean isIndoor() {
        return indoor;
    }
}
