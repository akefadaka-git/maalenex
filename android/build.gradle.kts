buildscript {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
    dependencies {
        // AGP 9.3.1 supplies KGP 2.2.10 by default. Pin patched build-tool dependencies
        // on the shared buildscript classpath so transitive AGP dependencies resolve safely.
        classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:2.4.21")
        classpath("com.google.guava:guava:33.7.2")
        classpath("org.apache.commons:commons-lang3:3.18.0")
        classpath("org.bitbucket.b_c:jose4j:0.9.6")
        classpath("org.bouncycastle:bcpkix-jdk18on:1.85")
        classpath("org.bouncycastle:bcprov-jdk18on:1.85")
        classpath("org.jdom:jdom2:2.0.6.1")
    }
}

plugins {
    id("com.android.application") version "9.3.1" apply false
}
