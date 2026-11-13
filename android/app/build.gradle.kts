import org.gradle.api.tasks.Sync

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val frontendDist = rootProject.layout.projectDirectory.dir("../frontend/dist")

android {
    namespace = "com.maalenex.moto"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.maalenex.moto"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    sourceSets.getByName("main").assets.srcDir(layout.buildDirectory.dir("generated/web-assets"))
}

tasks.register<Sync>("syncWebAssets") {
    from(frontendDist)
    into(layout.buildDirectory.dir("generated/web-assets/www"))
    doFirst {
        if (!frontendDist.asFile.exists()) {
            throw GradleException("Frontend build is missing. Run npm install and npm run build in ../frontend before assembling the Android app.")
        }
    }
}

tasks.named("preBuild").configure {
    dependsOn("syncWebAssets")
}

dependencies {
    implementation("androidx.webkit:webkit:1.12.1")
    implementation("androidx.core:core-ktx:1.15.0")
}
