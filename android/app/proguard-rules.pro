# Release builds are shrunk with R8. The libraries bring their own rules (OkHttp, coroutines,
# kotlinx.serialization); these keep the generated JSON readers of Groschen's own models.
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.**

-keepclassmembers @kotlinx.serialization.Serializable class io.github.mki002.groschen.** {
    *** Companion;
    kotlinx.serialization.KSerializer serializer(...);
}
-keep,includedescriptorclasses class io.github.mki002.groschen.**$$serializer { *; }
