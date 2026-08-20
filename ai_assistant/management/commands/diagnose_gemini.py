"""
Django management command to diagnose Gemini API models
Usage: python manage.py diagnose_gemini
"""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Diagnose available Gemini models'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write("GEMINI API MODEL DIAGNOSTIC")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Get API key
        api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        if not api_key or api_key == 'your_gemini_api_key_here':
            self.stdout.write(self.style.ERROR("GEMINI_API_KEY not configured"))
            return

        self.stdout.write(f"API_KEY_CONFIGURED: YES")
        self.stdout.write(f"API_KEY_LENGTH: {len(api_key)}")
        self.stdout.write("")

        # Import SDK
        try:
            from google.genai import Client
            self.stdout.write("SDK: google-genai")
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f"Cannot import: {e}"))
            return

        self.stdout.write("")
        self.stdout.write("Connecting to Gemini API...")

        try:
            client = Client(api_key=api_key)
            self.stdout.write(self.style.SUCCESS("✓ Client created"))
            self.stdout.write("")
            
            self.stdout.write("Listing available models...")
            self.stdout.write("-" * 70)
            
            models = list(client.models.list())
            
            if not models:
                self.stdout.write(self.style.WARNING("No models returned"))
                return
            
            self.stdout.write(f"Total models: {len(models)}")
            self.stdout.write("")
            
            text_gen_models = []
            
            for idx, model in enumerate(models):
                self.stdout.write(f"Model #{idx + 1}:")
                
                # Get model name
                if hasattr(model, 'name'):
                    model_name = model.name
                    self.stdout.write(f"  name: {model_name}")
                else:
                    model_name = str(model)
                    self.stdout.write(f"  name: {model_name} (from str)")
                
                # Get supported methods
                if hasattr(model, 'supported_actions'):
                    actions = model.supported_actions
                    self.stdout.write(f"  actions: {actions}")
                    
                    if 'generateContent' in actions:
                        text_gen_models.append(model_name)
                        self.stdout.write(self.style.SUCCESS("  ✓ SUPPORTS generateContent"))
                else:
                    self.stdout.write("  actions: NOT AVAILABLE")
                
                self.stdout.write("")
            
            self.stdout.write("-" * 70)
            self.stdout.write("")
            self.stdout.write(f"Text generation models: {len(text_gen_models)}")
            
            if text_gen_models:
                self.stdout.write("")
                self.stdout.write("AVAILABLE TEXT GENERATION MODELS:")
                for m in text_gen_models:
                    self.stdout.write(f"  - {m}")
                
                # Select best
                if 'models/gemini-2.5-flash' in text_gen_models:
                    selected = 'models/gemini-2.5-flash'
                elif any('2.5' in m and 'flash' in m for m in text_gen_models):
                    selected = next(m for m in text_gen_models if '2.5' in m and 'flash' in m)
                else:
                    flash_models = [m for m in text_gen_models if 'flash' in m.lower()]
                    selected = flash_models[0] if flash_models else text_gen_models[0]
                
                self.stdout.write("")
                self.stdout.write(self.style.SUCCESS(f"SELECTED_MODEL: {selected}"))
                self.stdout.write("")
                
                # Test
                self.stdout.write(f"Testing '{selected}' with 'Hi'...")
                try:
                    response = client.models.generate_content(
                        model=selected,
                        contents='Hi',
                        config={'max_output_tokens': 50, 'temperature': 0.7}
                    )
                    
                    result_text = None
                    if hasattr(response, 'text') and response.text:
                        result_text = response.text.strip()
                    elif hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            parts_text = ''.join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                            result_text = parts_text.strip()
                    
                    if result_text:
                        self.stdout.write(self.style.SUCCESS("✓ SUCCESS!"))
                        self.stdout.write(f"Response: {result_text[:100]}")
                        self.stdout.write("")
                        self.stdout.write("=" * 70)
                        self.stdout.write("FINAL RESULTS:")
                        self.stdout.write("=" * 70)
                        self.stdout.write(f"SDK_VERSION: google-genai (installed)")
                        self.stdout.write(f"AVAILABLE_MODELS: {', '.join(text_gen_models)}")
                        self.stdout.write(f"SELECTED_MODEL: {selected}")
                        self.stdout.write(f"MODEL_SUPPORTS_TEXT_GENERATION: YES")
                        self.stdout.write(f"API_CONNECTION: PASS")
                        self.stdout.write(f"CHAT_TEST: PASS")
                        self.stdout.write(f"ROOT_CAUSE: NONE")
                    else:
                        self.stdout.write(self.style.ERROR("Empty response"))
                        self.stdout.write(f"CHAT_TEST: FAIL")
                        self.stdout.write(f"ROOT_CAUSE: Model returned empty response")
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Test failed: {e}"))
                    self.stdout.write("")
                    self.stdout.write(f"AVAILABLE_MODELS: {', '.join(text_gen_models)}")
                    self.stdout.write(f"SELECTED_MODEL: {selected}")
                    self.stdout.write(f"CHAT_TEST: FAIL")
                    self.stdout.write(f"ROOT_CAUSE: {str(e)[:200]}")
            else:
                self.stdout.write(self.style.ERROR("No text generation models!"))
                self.stdout.write(f"ROOT_CAUSE: No text generation models available")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ERROR: {e}"))
            import traceback
            traceback.print_exc()
            self.stdout.write(f"ROOT_CAUSE: {str(e)[:200]}")
