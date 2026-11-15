buildscript {
    dependencies {
        // AGP 9.3.1 supplies KGP 2.2.10 for built-in Kotlin.
        // Override it with the patched, AGP-compatible KGP release.
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.4.21")
    }
}

plugins {
    id("com.android.application") version "9.3.1" apply false
}
