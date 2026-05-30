
#  ANALISIS STATISTIK DESKRIPTIF - ULASAN APK
# import library yang diperlukan
# pandas untuk manipulasi data, numpy untuk perhitungan statistik, 
# matplotlib dan seaborn untuk visualisasi, google_play_scraper untuk scraping ulasan, 
# datetime untuk manipulasi tanggal, dan warnings untuk mengabaikan peringatan.

import pandas as pd
import matplotlib.pyplot as plt
from google_play_scraper import reviews, Sort
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

#SCRAPING DATA
def scrape_ulasan(jumlah):

    print(f" Mengambil {jumlah} ulasan APK dari Google Play...")

    hasil, _ = reviews(
        'com.APK',             # App ID
        lang='id',                
        country='id',             
        sort=Sort.NEWEST,         # Sorting komen
        count=jumlah
    )

    df = pd.DataFrame(hasil)
    # Menampilkan kolom 
    print(df.columns.tolist()) 
    print(df.head(1))    
    # Pilih kolom yang relevan
    df = df[['userName', 'score', 'content', 'at', 'thumbsUpCount']]
    df.columns = ['nama', 'rating', 'ulasan', 'tanggal', 'likes']

    print(f" Berhasil mengambil {len(df)} ulasan!\n")
    return df

# PEMBERSIHAN DATA
# Fungsi ini membersihkan data dengan menghapus duplikat, nilai kosong, komen yang hanya berisi spasi dan koma

def bersihkan_data(df):

    print(" Membersihkan data...")
    awal = len(df)

    df = df.drop_duplicates()
    df = df.dropna(subset=['rating', 'ulasan'])
    df = df[df['ulasan'].str.strip() != '']
    df['nama'] = df['nama'].str.replace(',', '', regex=False).str.strip()

    print(f"   - Data awal  : {awal} baris")
    print(f"   - Data bersih: {len(df)} baris")
    print(f"   - Dihapus    : {awal - len(df)} baris\n")

    # Kategorisasi sentimen berdasarkan rating
    def kategori(r):
        if r >= 4:
            return 'Positif'
        elif r == 3:
            return 'Netral'
        else:
            return 'Negatif'

    df['sentimen'] = df['rating'].apply(kategori)
    return df



#  menghitung statistik deskriptif
def statistik_deskriptif(df):

    print("=" * 50)
    print("STATISTIK DESKRIPTIF RATING APK")
    print("=" * 50)

    rating = df['rating']

    mean    = rating.mean()  
    median  = rating.median()
    modus   = rating.mode()[0]
    std     = rating.std()  # Standar deviasi
    varians = rating.var()
    minimum = rating.min()
    maksimum = rating.max()
    q1      = rating.quantile(0.25)
    q3      = rating.quantile(0.75)
    iqr     = q3 - q1
    n       = len(rating)

    print(f"  Jumlah Data (n)     : {n}")
    print(f"  Mean (Rata-rata)    : {mean:.4f}")
    print(f"  Median              : {median:.1f}")
    print(f"  Modus               : {modus}")
    print(f"  Std. Deviasi        : {std:.4f}")
    print(f"  Varians             : {varians:.4f}")
    print(f"  Minimum             : {minimum}")
    print(f"  Maksimum            : {maksimum}")
    print(f"  Q1 (Kuartil 1)      : {q1}")
    print(f"  Q3 (Kuartil 3)      : {q3}")
    print(f"  IQR                 : {iqr}")
    print()

    # Distribusi frekuensi
    print("-" * 50)
    print(" DISTRIBUSI FREKUENSI RATING")
    print("-" * 50)
    frekuensi = rating.value_counts().sort_index()
    for r, f in frekuensi.items():
        persen = (f / n) * 100
        print(f"  bintang {r} : {f:4d} ulasan ({persen:5.1f}%) ")
    print()

    # Distribusi sentimen
    print("-" * 50)
    print("DISTRIBUSI SENTIMEN")
    print("-" * 50)
    sentimen = df['sentimen'].value_counts()
    for s, f in sentimen.items():
        persen = (f / n) * 100
        print(f"  {s:8s}: {f:4d} ulasan ({persen:5.1f}%)")
    print()

    return {
        'n': n, 'mean': mean, 'median': median, 'modus': modus,
        'std': std, 'varians': varians, 'min': minimum, 'max': maksimum,
        'q1': q1, 'q3': q3, 'iqr': iqr
    }



# membuat visualisasi data


def buat_visualisasi(df):

    print(" Membuat visualisasi...")

    # Pengaturan style
    plt.rcParams['font.family'] = 'DejaVu Sans'
    warna = ['#FF4B4B', '#FF8C42', '#FFC72C', '#5BC0EB', '#4CAF50']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Analisis Statistik Deskriptif\nUlasan - Google Play Store',
                 fontsize=16, fontweight='bold', y=1.01)

    # Grafik 1: Histogram Distribusi Rating
    ax1 = axes[0, 0]
    frekuensi = df['rating'].value_counts().sort_index()
    bars = ax1.bar(frekuensi.index, frekuensi.values, color=warna, edgecolor='white', linewidth=1.5)
    ax1.set_title('Distribusi Frekuensi Rating', fontweight='bold')
    ax1.set_xlabel('Rating (⭐)')
    ax1.set_ylabel('Jumlah Ulasan')
    ax1.set_xticks([1, 2, 3, 4, 5])
    for bar, val in zip(bars, frekuensi.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 str(val), ha='center', va='bottom', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Grafik 2: Pie Chart Sentimen
    ax2 = axes[0, 1]
    sentimen_count = df['sentimen'].value_counts()
    warna_sentimen = {'Positif': '#4CAF50', 'Netral': '#FFC72C', 'Negatif': '#FF4B4B'}
    colors = [warna_sentimen[s] for s in sentimen_count.index]
    wedges, texts, autotexts = ax2.pie(
        sentimen_count.values,
        labels=sentimen_count.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for autotext in autotexts:
        autotext.set_fontweight('bold')
    ax2.set_title('Proporsi Sentimen Pengguna', fontweight='bold')

    # Grafik 3: Tren Rating per Hari
    ax3 = axes[1, 0]
    df_hari = df.set_index('tanggal')
    tren_hari = df_hari['rating'].resample('D').mean().reset_index()
    tren_hari.columns = ['hari', 'rating']
    tren_hari = tren_hari.dropna()                # Hapus hari tanpa komen
    tren_hari['label'] = tren_hari['hari'].dt.strftime('%d %b %Y')
    tren_tail = tren_hari.tail(12)                  
 
    ax3.plot(range(len(tren_tail)), tren_tail['rating'],
             marker='o', color='#5BC0EB', linewidth=2.5, markersize=6)
    ax3.fill_between(range(len(tren_tail)), tren_tail['rating'],
                     alpha=0.15, color='#5BC0EB')
    ax3.set_title('Tren Rata-rata Rating (per hari)', fontweight='bold')
    ax3.set_xlabel('Hari')
    ax3.set_ylabel('Rata-rata Rating')
    ax3.set_xticks(range(len(tren_tail)))
    ax3.set_xticklabels(tren_tail['label'], rotation=45, ha='right', fontsize=7)
    ax3.set_ylim(1, 5)
    ax3.axhline(y=df['rating'].mean(), color='red', linestyle='--',
                alpha=0.6, label=f'Mean = {df["rating"].mean():.2f}')
    ax3.legend()
    ax3.grid(alpha=0.3)

    # Grafik 4: Boxplot Rating per Sentimen
    ax4 = axes[1, 1]
    urutan = ['Negatif', 'Netral', 'Positif']
    data_box = [df[df['sentimen'] == s]['rating'].values for s in urutan]
    bp = ax4.boxplot(data_box, labels=urutan, patch_artist=True,
                     medianprops={'color': 'black', 'linewidth': 2})
    for patch, color in zip(bp['boxes'], ['#FF4B4B', '#FFC72C', '#4CAF50']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax4.set_title('Boxplot Rating per Kategori Sentimen', fontweight='bold')
    ax4.set_xlabel('Sentimen')
    ax4.set_ylabel('Rating')
    ax4.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('APK_visualisasi.png', dpi=150, bbox_inches='tight')
    print("Visualisasi disimpan sebagai 'APK_visualisasi.png'\n")
    plt.show()



# EKSPOR DATA


def ekspor_data(df, stats):

    # Simpan data mentah
    df.to_csv('APK_ulasan.csv', index=False, encoding='utf-8-sig')
    print("Data ulasan disimpan: APK_ulasan.csv")

    # Simpan ringkasan statistik
    ringkasan = pd.DataFrame({
        'Ukuran Statistik': [
            'Jumlah Data (n)', 'Mean', 'Median', 'Modus',
            'Std. Deviasi', 'Varians', 'Minimum', 'Maksimum',
            'Q1', 'Q3', 'IQR'
        ],
        'Nilai': [
            stats['n'], round(stats['mean'], 4), stats['median'], stats['modus'],
            round(stats['std'], 4), round(stats['varians'], 4),
            stats['min'], stats['max'],
            stats['q1'], stats['q3'], stats['iqr']
        ]
    })
    ringkasan.to_excel('APK_statistik.xlsx', index=False)
    print("Statistik disimpan  : APK_statistik.xlsx\n")


# MAIN PROGRAM

if __name__ == "__main__":
    print("  ANALISIS ULASAN - GOOGLE PLAY STORE")
    #pipeline
    df_raw    = scrape_ulasan(jumlah=1000)       # 1. Scraping
    df_bersih = bersihkan_data(df_raw)            # 2. Cleaning
    stats     = statistik_deskriptif(df_bersih)  # 3. Statistik
    buat_visualisasi(df_bersih)                   # 4. Visualisasi
    ekspor_data(df_bersih, stats)                 # 5. Ekspor

    print(" Analisis selesai!.\n")
