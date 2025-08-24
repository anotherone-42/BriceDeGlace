using System;
using Xamarin.Forms;
using System.Threading.Tasks;
using FFImageLoading.Forms;
using Newtonsoft.Json.Linq;

namespace BriceDeGlace
{
    public class MainPage : ContentPage
    {
        private readonly string[] rpi_addresses = {
            // IP locale WiFi
            "YOUR_RPI_ADRESS",     // IP locale Ethernet
            "YOUR_TAILSCALE_ADRESS"       // IP Tailscale
        };
        private string active_rpi_address;

        private TimePicker _midiTimePicker;
        private TimePicker _soirTimePicker;
        private Switch _midiSwitch;
        private Switch _soirSwitch;
        private Label _midiStatusLabel;
        private Label _soirStatusLabel;
        private Label _statusLabel;
        private Label _connectionLabel;
        private Label _iceMakerStatusLabel;
        private RefreshView _refreshView;

        public MainPage()
        {
            CreateInterface();
        }

        protected override async void OnAppearing()
        {   
            base.OnAppearing();

            var isConnected = await CheckConnection();
            if (isConnected)
            {
                _connectionLabel.Text = $"🟢 Connecté à la rpi ({active_rpi_address})";
                _connectionLabel.TextColor = Color.FromHex("#4CAF50");
                await LoadCurrentSchedule();
                await CheckIceMakerStatus();
            }
            else
            {
                _connectionLabel.Text = "🔴 Hors ligne";
                _connectionLabel.TextColor = Color.FromHex("#F44336");
            }
        }

        private void CreateInterface()
        {
            Title = "Brice de glace";
            BackgroundColor = Color.White;

            var mainGrid = new Grid();

            _refreshView = new RefreshView
            {
                RefreshColor = Color.FromHex("#1565C0")
            };

            _refreshView.Command = new Command(async () =>
            {
                await LoadCurrentSchedule();
                await CheckIceMakerStatus();
                _refreshView.IsRefreshing = false;
            });

            var scrollView = new ScrollView
            {
                VerticalScrollBarVisibility = ScrollBarVisibility.Always
            };

            var mainStack = new StackLayout
            {
                Padding = new Thickness(20),
                Spacing = 15
            };

            // Titre
            var titleLabel = new Label
            {
                Text = "🧊T'es glacé🧊",
                FontSize = 24,
                FontAttributes = FontAttributes.Bold,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center,
                Margin = new Thickness(0, 20, 0, 30)
            };
            mainStack.Children.Add(titleLabel);

            // Indicateur de connexion
            _connectionLabel = new Label
            {
                Text = "⚪ Vérification connexion...",
                FontSize = 14,
                HorizontalOptions = LayoutOptions.Center,
                Margin = new Thickness(0, -20, 0, 10)
            };
            mainStack.Children.Add(_connectionLabel);

            // Statut générateur de glaçons
            _iceMakerStatusLabel = new Label
            {
                Text = "🧊 Générateur: En attente du capteur...",
                FontSize = 12,
                HorizontalOptions = LayoutOptions.Center,
                TextColor = Color.FromHex("#FF9800"),
                Margin = new Thickness(0, -5, 0, 10)
            };
            mainStack.Children.Add(_iceMakerStatusLabel);

            // Frame Midi
            var midiFrame = new Frame
            {
                BackgroundColor = Color.White,
                CornerRadius = 15,
                Padding = new Thickness(20),
                HasShadow = true,
                Margin = new Thickness(0, 5, 0, 0)
            };

            var midiStack = new StackLayout { Spacing = 15 };

            midiStack.Children.Add(new Label
            {
                Text = "🌅 MIDI",
                FontSize = 20,
                FontAttributes = FontAttributes.Bold,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center
            });

            _midiTimePicker = new TimePicker
            {
                Time = new TimeSpan(12, 0, 0),
                FontSize = 18,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center
            };
            midiStack.Children.Add(_midiTimePicker);

            _midiSwitch = new Switch
            {
                IsToggled = true,
                HorizontalOptions = LayoutOptions.Center
            };
            midiStack.Children.Add(_midiSwitch);

            _midiStatusLabel = new Label
            {
                Text = "Activé",
                FontSize = 14,
                TextColor = Color.FromHex("#4CAF50"),
                HorizontalOptions = LayoutOptions.Center
            };
            midiStack.Children.Add(_midiStatusLabel);

            _midiSwitch.Toggled += (sender, e) =>
            {
                _midiStatusLabel.Text = e.Value ? "Activé" : "Désactivé";
                _midiStatusLabel.TextColor = e.Value ? Color.FromHex("#4CAF50") : Color.FromHex("#F44336");
            };

            midiFrame.Content = midiStack;
            mainStack.Children.Add(midiFrame);

            // Frame Soir
            var soirFrame = new Frame
            {
                BackgroundColor = Color.White,
                CornerRadius = 15,
                Padding = new Thickness(20),
                HasShadow = true
            };

            var soirStack = new StackLayout { Spacing = 15 };

            soirStack.Children.Add(new Label
            {
                Text = "🌙 SOIR",
                FontSize = 20,
                FontAttributes = FontAttributes.Bold,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center
            });

            _soirTimePicker = new TimePicker
            {
                Time = new TimeSpan(19, 0, 0),
                FontSize = 18,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center
            };
            soirStack.Children.Add(_soirTimePicker);

            _soirSwitch = new Switch
            {
                IsToggled = true,
                HorizontalOptions = LayoutOptions.Center
            };
            soirStack.Children.Add(_soirSwitch);

            _soirStatusLabel = new Label
            {
                Text = "Activé",
                FontSize = 14,
                TextColor = Color.FromHex("#4CAF50"),
                HorizontalOptions = LayoutOptions.Center
            };
            soirStack.Children.Add(_soirStatusLabel);

            _soirSwitch.Toggled += (sender, e) =>
            {
                _soirStatusLabel.Text = e.Value ? "Activé" : "Désactivé";
                _soirStatusLabel.TextColor = e.Value ? Color.FromHex("#4CAF50") : Color.FromHex("#F44336");
            };

            soirFrame.Content = soirStack;
            mainStack.Children.Add(soirFrame);

            // Boutons principaux
            var buttonStack = new StackLayout
            {
                Spacing = 15,
                Margin = new Thickness(0, 20, 0, 0)
            };

            // Ligne unique avec deux boutons
            var mainButtonStack = new StackLayout
            {
                Orientation = StackOrientation.Horizontal,
                HorizontalOptions = LayoutOptions.FillAndExpand,
                Spacing = 15
            };

            var saveButton = new Button
            {
                Text = "💾 Sauvegarder",
                BackgroundColor = Color.FromHex("#4CAF50"),
                TextColor = Color.White,
                FontSize = 16,
                FontAttributes = FontAttributes.Bold,
                CornerRadius = 15,
                HeightRequest = 60,
                HorizontalOptions = LayoutOptions.FillAndExpand
            };

            saveButton.Clicked += async (sender, e) =>
            {
                await AnimateButton(saveButton);
                await SaveSchedule();
            };
            mainButtonStack.Children.Add(saveButton);

            var testButton = new Button
            {
                Text = "test moteur",
                BackgroundColor = Color.FromHex("#FF5722"),
                TextColor = Color.White,
                FontSize = 16,
                FontAttributes = FontAttributes.Bold,
                CornerRadius = 15,
                HeightRequest = 60,
                HorizontalOptions = LayoutOptions.FillAndExpand
            };

            testButton.Clicked += async (sender, e) =>
            {
                await AnimateButton(testButton);
                await TestServo();
            };
            mainButtonStack.Children.Add(testButton);

            buttonStack.Children.Add(mainButtonStack);
            mainStack.Children.Add(buttonStack);

            // Status
            _statusLabel = new Label
            {
                Text = "Prêt",
                FontSize = 16,
                TextColor = Color.FromHex("#1565C0"),
                HorizontalOptions = LayoutOptions.Center,
                Margin = new Thickness(0, 20, 0, 0)
            };
            mainStack.Children.Add(_statusLabel);

            scrollView.Content = mainStack;
            _refreshView.Content = scrollView;
            mainGrid.Children.Add(_refreshView);

            // GIF de Brice
            var frontBriceGif = new CachedImage
            {
                Source = "brice_de_nice.gif",
                Aspect = Aspect.AspectFit,
                Opacity = 0.1,
                VerticalOptions = LayoutOptions.Start,
                HorizontalOptions = LayoutOptions.Center,
                WidthRequest = 396,
                HeightRequest = 594,
                Margin = new Thickness(0, 25, 0, 0),
                InputTransparent = true,
                BackgroundColor = Color.Transparent,
                DownsampleToViewSize = true
            };

            mainGrid.Children.Add(frontBriceGif);
            Content = mainGrid;
        }

        private async Task<bool> CheckConnection()
        {
            foreach (var address in rpi_addresses)
            {
                try
                {
                    System.Diagnostics.Debug.WriteLine($"Tentative de connexion à {address}...");
                    using (var client = new System.Net.Http.HttpClient())
                    {
                        client.Timeout = TimeSpan.FromSeconds(3);
                        var response = await client.GetAsync($"http://{address}:5000/test");
                        if (response.IsSuccessStatusCode)
                        {
                            active_rpi_address = address;
                            System.Diagnostics.Debug.WriteLine($"Connexion réussie avec {address}");
                            return true;
                        }
                        System.Diagnostics.Debug.WriteLine($"Échec connexion {address}: {response.StatusCode}");
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Erreur connexion {address}: {ex.Message}");
                    continue;
                }
            }
            return false;
        }

        private async Task LoadCurrentSchedule()
        {
            try
            {
                _statusLabel.Text = "Chargement des horaires...";
                _statusLabel.TextColor = Color.FromHex("#FF9800");

                using (var client = new System.Net.Http.HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(10);
                    var response = await client.GetAsync($"http://{active_rpi_address}:5000/api/schedule");

                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        var scheduleData = JObject.Parse(json);

                        if (scheduleData["status"]?.ToString() == "success")
                        {
                            var schedule = scheduleData["schedule"];

                            // Midi
                            var midiTime = schedule["midi"]["time"].ToString();
                            var midiEnabled = (bool)schedule["midi"]["enabled"];
                            _midiTimePicker.Time = TimeSpan.Parse(midiTime);
                            _midiSwitch.IsToggled = midiEnabled;

                            // Soir
                            var soirTime = schedule["soir"]["time"].ToString();
                            var soirEnabled = (bool)schedule["soir"]["enabled"];
                            _soirTimePicker.Time = TimeSpan.Parse(soirTime);
                            _soirSwitch.IsToggled = soirEnabled;

                            _statusLabel.Text = "Horaires chargés ✅";
                            _statusLabel.TextColor = Color.FromHex("#4CAF50");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _statusLabel.Text = "Impossible de charger les horaires";
                _statusLabel.TextColor = Color.FromHex("#F44336");
                System.Diagnostics.Debug.WriteLine($"Erreur chargement: {ex.Message}");
            }
        }

        private async Task SaveSchedule()
        {
            try
            {
                var midiTime = _midiTimePicker.Time;
                var soirTime = _soirTimePicker.Time;
                var midiEnabled = _midiSwitch.IsToggled;
                var soirEnabled = _soirSwitch.IsToggled;

                await SendScheduleToRaspberryPi(midiTime, soirTime, midiEnabled, soirEnabled);

                _statusLabel.Text = "Horaires sauvegardés !";
                _statusLabel.TextColor = Color.FromHex("#4CAF50");

                await DisplayAlert("Succès", "Horaires sauvegardés !", "OK");
            }
            catch (Exception ex)
            {
                _statusLabel.Text = $"Erreur: {ex.Message}";
                _statusLabel.TextColor = Color.FromHex("#F44336");
                await DisplayAlert("Erreur", ex.Message, "OK");
            }
        }

        private async Task TestServo()
        {
            try
            {
                _statusLabel.Text = "test servo";
                _statusLabel.TextColor = Color.FromHex("#FF9800");

                await CallRaspberryPiAPI("test");

                _statusLabel.Text = "Ca marche mdr";
                _statusLabel.TextColor = Color.FromHex("#4CAF50");

                await DisplayAlert("Test", "Servo actionné avec succès !", "OK");
            }
            catch (Exception ex)
            {
                _statusLabel.Text = $"Erreur: {ex.GetType().Name}";
                _statusLabel.TextColor = Color.FromHex("#F44336");
                await DisplayAlert("Erreur", $"Problème de connexion:\n{ex.Message}", "OK");
            }
        }

        private async Task CheckIceMakerStatus()
        {
            try
            {
                using (var client = new System.Net.Http.HttpClient())
                {
                    client.Timeout = TimeSpan.FromSeconds(5);
                    var response = await client.GetAsync($"http://{active_rpi_address}:5000/api/ice_maker/status");

                    if (response.IsSuccessStatusCode)
                    {
                        var json = await response.Content.ReadAsStringAsync();
                        var data = JObject.Parse(json);

                        var ledState = data["ice_maker_led"]?.ToString();
                        var message = data["message"]?.ToString();

                        switch (ledState)
                        {
                            case "ON":
                                _iceMakerStatusLabel.Text = "🧊 Générateur: ✅ EN MARCHE";
                                _iceMakerStatusLabel.TextColor = Color.FromHex("#4CAF50");
                                break;
                            case "OFF":
                                _iceMakerStatusLabel.Text = "🧊 Générateur: ❌ ARRÊTÉ";
                                _iceMakerStatusLabel.TextColor = Color.FromHex("#F44336");
                                break;
                            default:
                                _iceMakerStatusLabel.Text = $"🧊 {message ?? "Statut inconnu"}";
                                _iceMakerStatusLabel.TextColor = Color.FromHex("#FF9800");
                                break;
                        }
                    }
                }
            }
            catch
            {
                _iceMakerStatusLabel.Text = "🧊 Générateur: Erreur de connexion";
                _iceMakerStatusLabel.TextColor = Color.FromHex("#F44336");
            }
        }

        private async Task SendScheduleToRaspberryPi(TimeSpan midiTime, TimeSpan soirTime, bool midiEnabled, bool soirEnabled)
        {
            using (var client = new System.Net.Http.HttpClient())
            {
                client.Timeout = TimeSpan.FromSeconds(30);

                var schedule = new
                {
                    midi = new
                    {
                        time = midiTime.ToString(@"hh\:mm"),
                        enabled = midiEnabled
                    },
                    soir = new
                    {
                        time = soirTime.ToString(@"hh\:mm"),
                        enabled = soirEnabled
                    }
                };

                var json = Newtonsoft.Json.JsonConvert.SerializeObject(schedule);
                var content = new System.Net.Http.StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await client.PostAsync($"http://{active_rpi_address}:5000/api/schedule", content);
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    throw new Exception($"Erreur serveur: {response.StatusCode}");
                }

                var result = JObject.Parse(responseContent);
                if (result["status"]?.ToString() != "success")
                {
                    throw new Exception($"Erreur: {result["message"]}");
                }
            }
        }

        private async Task CallRaspberryPiAPI(string action)
        {
            using (var client = new System.Net.Http.HttpClient())
            {
                client.Timeout = TimeSpan.FromSeconds(30);

                var url = $"http://{active_rpi_address}:5000/api/servo/press";
                var json = $"{{\"action\": \"{action}\"}}";
                var content = new System.Net.Http.StringContent(json, System.Text.Encoding.UTF8, "application/json");

                var response = await client.PostAsync(url, content);
                var responseContent = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    throw new Exception($"Erreur {response.StatusCode}: {responseContent}");
                }
            }
        }

        private async Task AnimateButton(Button button)
        {
            await button.ScaleTo(0.95, 100);
            await button.ScaleTo(1.0, 100);
        }
    }
}