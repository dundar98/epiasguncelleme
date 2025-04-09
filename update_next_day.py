import pandas as pd
from eptr2 import EPTR2
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from supabase import create_client, Client

load_dotenv()

# Supabase yapılandırması
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_next_day_data():
    try:
        # EPIAS bağlantısı
        eptr = EPTR2(
            username=os.getenv('EPIAS_USERNAME'),
            password=os.getenv('EPIAS_PASSWORD')
        )
        
        # Yarının tarihini al
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"Yarın ({tomorrow}) için veri çekiliyor...")
        
        # Sadece yarının verisi için çağrı yap
        df = eptr.call(
            "mcp",
            start_date=tomorrow,
            end_date=tomorrow
        )
        
        if df is not None and not df.empty:
            # Veri düzenleme
            df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
            df['hour'] = df['hour'].str.split(':').str[0].astype(int)
            df = df.sort_values('date')
            
            # String'e çevir
            df['date'] = df['date'].astype(str)
            
            # Supabase'e kaydet
            data = df.to_dict(orient='records')
            response = supabase.table("ptf_data").insert(data).execute()
            
            if hasattr(response, 'error') and response.error:
                print(f"Hata: {response.error}")
            else:
                print(f"Yarının verileri başarıyla eklendi. Toplam: {len(df)} kayıt")
        else:
            print("Yarın için veri henüz mevcut değil")
            
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    fetch_next_day_data()
