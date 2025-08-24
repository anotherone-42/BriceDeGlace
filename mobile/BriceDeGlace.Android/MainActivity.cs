using Android.App;
using Android.OS;
using FFImageLoading.Forms.Platform;

namespace BriceDeGlace.Android
{
    [Activity(Label = "Brice de glace", MainLauncher = true, Theme = "@android:style/Theme.Material.Light.NoActionBar")]
    public class MainActivity : global::Xamarin.Forms.Platform.Android.FormsApplicationActivity
    {
        protected override void OnCreate(Bundle savedInstanceState)
        {
            base.OnCreate(savedInstanceState);

            global::Xamarin.Forms.Forms.Init(this, savedInstanceState);

            CachedImageRenderer.Init(enableFastRenderer: true);

            // Créer une app simple sans Shell
            var app = new global::Xamarin.Forms.Application();
            app.MainPage = new global::Xamarin.Forms.NavigationPage(new BriceDeGlace.MainPage())
            {
                Title = "Brice de glace"
            };

            LoadApplication(app);
        }
    }
}