import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.compose)
}

// The build on GitHub sets the version; a build on your own computer is "dev".
val buildNumber = providers.environmentVariable("GROSCHEN_BUILD_NUMBER").orNull?.toIntOrNull() ?: 1
val buildName = providers.environmentVariable("GROSCHEN_VERSION_NAME").orNull ?: "dev"

// The signing key never lives in the repository: GitHub writes it from a secret into a file
// for the release build and deletes it afterwards (see .github/workflows/android.yml).
val keystoreFile = providers.environmentVariable("GROSCHEN_KEYSTORE").orNull?.let(::file)
val keystorePassword = providers.environmentVariable("GROSCHEN_KEYSTORE_PASSWORD").orNull

android {
    namespace = "io.github.mki002.groschen"
    compileSdk = 37

    defaultConfig {
        applicationId = "io.github.mki002.groschen"
        // Android 11: the fingerprint dialog and the phone's key store that the login needs.
        minSdk = 30
        targetSdk = 36
        versionCode = buildNumber
        versionName = buildName
    }

    signingConfigs {
        if (keystoreFile != null && keystorePassword != null) {
            create("release") {
                storeFile = keystoreFile
                storePassword = keystorePassword
                keyAlias = "groschen"
                keyPassword = keystorePassword
            }
        }
    }

    buildTypes {
        getByName("debug") {
            applicationIdSuffix = ".debug"
        }
        getByName("release") {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.findByName("release")
        }
    }

    kotlin {
        compilerOptions {
            jvmTarget = JvmTarget.fromTarget("17")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging.resources {
        excludes += "/META-INF/{AL2.0,LGPL2.1}"
    }
}

dependencies {
    val composeBom = platform(libs.androidx.compose.bom)
    implementation(composeBom)
    implementation(libs.androidx.compose.foundation)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.process)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.okhttp)

    testImplementation(libs.junit)
    testImplementation(libs.kotlin.test)
    testImplementation(libs.okhttp.mockwebserver)
}

// The libraries inside the app, written to app/gradle.lockfile when asked for
// (`./gradlew :app:dependencies --write-locks`), so the build on GitHub can check them
// for known vulnerabilities. Without that file nothing is pinned.
configurations.matching { it.name == "releaseRuntimeClasspath" }.configureEach {
    resolutionStrategy.activateDependencyLocking()
}
