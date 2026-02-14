import os
import sys

def analyze(path='datos_sinteticos.csv'):
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
    except Exception as e:
        print('Faltan paquetes requeridos. Instala: pandas, matplotlib, seaborn')
        print('Por ejemplo: pip install pandas matplotlib seaborn')
        return 1

    # localizar archivo si nombre escrito con error
    if not os.path.exists(path):
        alt = 'datos_siteticos.csv'
        if os.path.exists(alt):
            path = alt
        else:
            print(f'No se encontró el archivo `{path}` ni `{alt}` en el directorio actual.')
            return 1

    df = pd.read_csv(path, parse_dates=[c for c in ['fecha_campana'] if c in pd.read_csv(path, nrows=0).columns])

    out_dir = 'analysis_output'
    os.makedirs(out_dir, exist_ok=True)

    print('\n--- Resumen general ---')
    print('Archivo:', path)
    print('Filas x Columnas:', df.shape)
    print('\nColumnas y tipos:')
    print(df.dtypes)

    print('\n--- Primeras filas ---')
    with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
        print(df.head(10).to_string(index=False))

    print('\n--- Estadísticas descriptivas ---')
    desc = df.describe(include='all')
    print(desc)
    desc.to_csv(os.path.join(out_dir, 'descriptive_stats.csv'))

    print('\n--- Valores faltantes por columna ---')
    missing = df.isnull().sum()
    print(missing[missing > 0])
    missing.to_csv(os.path.join(out_dir, 'missing_values.csv'))

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    if num_cols:
        print('\n--- Correlación (numérica) ---')
        corr = df[num_cols].corr()
        print(corr)
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
        plt.title('Correlación entre variables numéricas')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, 'correlation_heatmap.png'))
        plt.close()

        # histogramas
        for col in num_cols:
            plt.figure()
            sns.histplot(df[col].dropna(), kde=True)
            plt.title(f'Histograma: {col}')
            plt.tight_layout()
            safe_col = col.replace(' ', '_')
            plt.savefig(os.path.join(out_dir, f'hist_{safe_col}.png'))
            plt.close()

    if cat_cols:
        print('\n--- Resumen columnas categóricas ---')
        for col in cat_cols:
            print(f'\nColumna: {col}')
            vc = df[col].value_counts(dropna=False).head(10)
            print(vc)
            plt.figure(figsize=(6, 4))
            vc.plot(kind='bar')
            plt.title(f'Ventas: {col}')
            plt.tight_layout()
            safe_col = col.replace(' ', '_')
            plt.savefig(os.path.join(out_dir, f'cat_{safe_col}.png'))
            plt.close()

    # estadísticas numéricas por campaña o segmento si existen columnas clave
    if 'campana_id' in df.columns and 'revenue_generado' in df.columns:
        agg = df.groupby('campana_id')[['revenue_generado', 'costo_total']].sum()
        agg['roas_calc'] = agg['revenue_generado'] / agg['costo_total'].replace({0: pd.NA})
        agg.to_csv(os.path.join(out_dir, 'aggregate_by_campaign.csv'))

    print(f'Análisis y gráficos guardados en: {out_dir}')
    return 0


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'datos_sinteticos.csv'
    rc = analyze(path)
    sys.exit(rc)
