import altair as alt
import polars as pl
import pandas as pd


class Grafici:
    """
    In questa classe creo le funzioni per la stampa dei grafici
    così da standardizzare il più possibile

    Includo anche @staticmethod alle funzioni cosicché non abbiano bisogno dell'argomento self
    """

    @staticmethod
    def crea_grafico_linea(dat,
                           x_col: str,
                           y_col: str,
                           color_col: str = None,
                           title: str = None,
                           width: int = 800,
                           height: int = 400,
                           totale: bool = False,
                           label_angle: int = 0,
                           show_legend: bool = True):
        """
        grafico per la stampa di scatterplot adattoa dati temporali, con unione dein punti con linee
        """
        base = alt.Chart(dat).mark_line(point=True).encode(
            x=alt.X(f"{x_col}:O", title=x_col.title(), axis=alt.Axis(labelAngle=label_angle)),
            # Applicazione dell'angolo etichette
            y=alt.Y(f"{y_col}:Q", title=y_col.title()),
            tooltip=[
                alt.Tooltip(f"{x_col}:O"),
                alt.Tooltip(f"{y_col}:Q"),
                alt.Tooltip("Percentuale:Q", format=".2f", title="% sul totale"),
                alt.Tooltip(f"{color_col}:N")
            ]
        ).properties(
            width=width,
            height=height,
            title={
                'text': title or f"{y_col} by {x_col}",
                'anchor': 'middle'
            }
        )

        if color_col == "Sex" and not totale:
            base = base.encode(
                color=alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male'],
                        range=['#e377c2', '#1f77b4']
                    ),
                    legend=alt.Legend(title=color_col.title(), orient='right',
                                      columnPadding=10) if show_legend else None
                )
            )
        elif color_col == "Sex" and totale:
            base = base.encode(
                color=alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male', 'Total'],
                        range=['#e377c2', '#1f77b4', 'black']
                    ),
                    legend=alt.Legend(title=color_col.title(), orient='right',
                                      columnPadding=10) if show_legend else None
                )
            )
        else:
            base = base.encode(color=alt.Color(f"{color_col}:N",
                                               legend=alt.Legend(title=color_col.title(), orient='right',
                                               columnPadding=10) if show_legend else None)
                               )

        # Highlight con barra verticale
        highlight = alt.selection_single(
            on='mouseover',
            fields=[x_col],
            nearest=True
        )

        punti_highlight = base.mark_point(size=100, filled=True).encode(
            opacity=alt.condition(highlight, alt.value(1), alt.value(0))
        ).add_selection(highlight)

        barra_hover = alt.Chart(dat).mark_rule(color='gray').encode(
            x=alt.X(f"{x_col}:O"),
            size=alt.condition(highlight, alt.value(2), alt.value(0))
        ).transform_filter(highlight)

        grafico = base + punti_highlight + barra_hover

        # calcolo del totale per anno
        if totale:
            totale_annuale = (
                dat.group_by(x_col)
                .agg(pl.sum(y_col).alias("Totale"))
                .with_columns(pl.lit("Total").alias(color_col))
            )

            linea_totale = (
                alt.Chart(totale_annuale).mark_line(point=True).encode(
                    x=alt.X(f"{x_col}:O"),
                    y=alt.Y("Totale:Q"),
                    color=alt.Color(
                        f"{color_col}:N",
                        scale=alt.Scale(
                            domain=['Female', 'Male', 'Total'],
                            range=['#e377c2', '#1f77b4', 'black']
                        ),
                        legend=alt.Legend(title=color_col.title(), orient='right',
                                          columnPadding=10) if show_legend else None
                    ),
                    tooltip=[
                        alt.Tooltip(f"{x_col}:O"),
                        alt.Tooltip("Totale:Q")
                    ]
                )
            )
            grafico = grafico + linea_totale

        return grafico


    @staticmethod
    def crea_grafico_barre(dat,
                           x_col: str,
                           y_col: str,
                           color_col: str = None,
                           sort: str = "-y",
                           horizontal: bool = False,
                           width: int = 700,
                           height: int = 400,
                           title: str = None,
                           add_text: bool = True,
                           show_legend: bool = True,
                           label_angle: int = 0):
        """
        grafici a barre interattivi e personalizzati con barre affiancate,highlight selettivi.
        """
        if horizontal:
            x_encoding = alt.X(f"{y_col}:Q", title=y_col.title())
            y_encoding = alt.Y(f"{x_col}:N", title=x_col.title(), sort=sort)
        else:
            x_encoding = alt.X(f"{x_col}:N", title=x_col.title(), sort=sort, axis=alt.Axis(labelAngle=label_angle))
            y_encoding = alt.Y(f"{y_col}:Q", title=y_col.title())

        encoding = {'x': x_encoding, 'y': y_encoding}

        if color_col:
            if color_col == "Sex":
                encoding['color'] = alt.Color(
                    f"{color_col}:N",
                    scale=alt.Scale(
                        domain=['Female', 'Male'],
                        range=['#e377c2', '#1f77b4']
                    ),
                    legend=alt.Legend(title="Legenda") if show_legend else None
                )
                encoding['xOffset'] = alt.XOffset(f"{color_col}:N")
            else:
                encoding["color"] = alt.Color(
                    f"{color_col}:Q",
                    legend=alt.Legend(title="Legenda") if show_legend else None
                )

        # evidenziatore quando passsso sopra la pbarra
        highlight = alt.selection_point(
            on='mouseover',
            nearest=False,
            fields=[x_col, color_col],
            resolve="global"
        )

        # Tooltip personalizzato
        tooltip = [
            alt.Tooltip(x_col, title="Anno"),
            alt.Tooltip(y_col, title="Morti", format=","),
        ]
        if color_col:
            tooltip.append(alt.Tooltip(color_col, title="Categoria"))

        # Grafico base con highlight sui bordi
        grafico = (
            alt.Chart(dat)
            .mark_bar(strokeWidth=2)
            .encode(
                **encoding,
                tooltip=tooltip,
                opacity=alt.condition(highlight, alt.value(1), alt.value(0.6)),
                stroke=alt.condition(highlight, alt.value('black'), alt.value(None))
            )
            .properties(
                width=width,
                height=height,
                title={'text': title or f"{y_col} by {x_col}", 'anchor': 'middle'}
            )
            .add_selection(highlight)
        )

        # Aggiunta delle etichette sopra ogni barra
        if add_text:
            text_encoding = {
                'text': alt.Text(f"{y_col}:Q", format=","),
                'opacity': alt.condition(highlight, alt.value(1), alt.value(0.6))
            }
            if color_col:
                text_encoding['xOffset'] = alt.XOffset(f"{color_col}:N")

            etichette_grafico = (
                alt.Chart(dat)
                .mark_text(
                    align='left' if horizontal else "center",
                    baseline='middle' if horizontal else "bottom",
                    dy=0 if horizontal else -5,
                    dx=5 if horizontal else 0
                )
                .encode(
                    x=x_encoding,
                    y=y_encoding,
                    **text_encoding
                )
            )

            grafico = grafico + etichette_grafico

        return grafico


    @staticmethod
    def create_grafico_torta(dat, category_col: str, value_col: str, title: str = None,
                             width: int = 600, height: int = 300, inner_radius: int = 50,
                             show_legend: bool = True):
        """
        grafico a torta
        """
        total = dat.get_column(value_col).sum()  # calcoliamo il totale qui
        dat = dat.with_columns(
            (pl.col(value_col) / total * 100).round(1).alias('percentage'),
            (pl.col(value_col).cast(pl.Utf8)).alias('total_str')
        )

        # Configurazione colori condizionali
        if category_col == "Sex":
            color_scale = alt.Scale(domain=["Female", "Male"], range=['#e377c2', '#1f77b4'])
        else:
            color_scale = alt.Scale(scheme='category20')

        # Selezione per highlight (per il grafico, non per le etichette)
        highlight = alt.selection_point(
            name='select',
            on='mouseover',
            fields=[category_col]
        )

        # Grafico base con highlight separati
        pie = alt.Chart(dat).mark_arc(innerRadius=inner_radius).encode(
            theta=alt.Theta(f"{value_col}:Q", stack=True),
            color=alt.Color(f"{category_col}:N", scale=color_scale,
                            legend=alt.Legend(title="Legenda", orient='right') if show_legend else None),
            tooltip=[
                alt.Tooltip(category_col, title="Categoria"),
                alt.Tooltip('percentage', title="Percentuale", format='.1f')
            ]
        ).properties(
            width=width,
            height=height,
            title={
                'text': title or f"{value_col} by {category_col}",
                'anchor': 'middle'
            }
        ).add_selection(highlight).encode(
            opacity=alt.condition(highlight, alt.value(1), alt.value(0.6)),
            stroke=alt.condition(highlight, alt.value('black'), alt.value('transparent')),
            strokeWidth=alt.condition(highlight, alt.value(2), alt.value(0))  # spessore del bordo
        )

        # etichette con totali interi sopra ciascuna fetta, colorate in base alla fetta
        text = pie.mark_text(
            size=14,
            fontWeight='normal'  # Rimuove il grassetto
        ).encode(
            text=alt.Text('total_str:N', format=',.0f'),  # Aggiunge il separatore delle migliaia
            theta=alt.Theta(f"{value_col}:Q", stack=True),
            radius=alt.value(inner_radius + 90),
            color=alt.Color(f"{category_col}:N", scale=color_scale),
            opacity=alt.value(1)  # Mantiene l'opacità costante per tutte le etichette
        )

        # aggiung il totale al centro
        total_text = alt.Chart(pd.DataFrame([{'total': total}])).mark_text(
            size=20,
            fontWeight='normal',
            align='center',
            baseline='middle'
        ).encode(
            text=alt.Text('total:Q', format=',.0f')  #separatore delle migliaia
        ).properties(
            width=width,
            height=height
        )

        return pie + text + total_text

    @staticmethod
    def crea_boxplot(dat, x_col: str, y_col: str, title: str = None, width: int = 800, height: int = 500,
                     label_angle: int = -30, show_legend: bool = True):
        """
        Creazione di boxplot
        """
        color_encoding = None

        # Aggiunta della condizione per la colonna "Sex"
        if x_col == "Sex":
            color_encoding = alt.Color(
                f"{x_col}:N",
                scale=alt.Scale(
                    domain=["Male", "Female"],
                    range=["#1f77b4", "#e377c2"]  # Blu per Male, Rosa per Female
                ),
                legend=alt.Legend(title="Legenda") if show_legend else None  # Mostra o nasconde la legenda
            )

        boxplot = (
            alt.Chart(dat)
            .mark_boxplot(extent="min-max",
                          size=30)  # Usa l'intervallo completo min-max e rende i boxplot più "cicciotti"
            .encode(
                x=alt.X(f"{x_col}:N", title=x_col.title(), axis=alt.Axis(labelAngle=label_angle)),
                y=alt.Y(f"{y_col}:Q", title=y_col.title()),
                tooltip=[
                    alt.Tooltip(f"{x_col}:N", title="Categoria"),
                    alt.Tooltip(f"{y_col}:Q", title="Valore")
                ],
                color=color_encoding  # Aggiunge l'encoding del color
            )
            .configure_boxplot(
                box=alt.MarkConfig(size=50),  # Configura la dimensione delle box
                rule=alt.MarkConfig(size=3),  # Configura la dimensione delle linee
                median=alt.MarkConfig(size=4)  # Configura la dimensione della linea mediana
            )
            .properties(
                width=width,
                height=height,
                title=title or f"Distribuzione di {y_col} per {x_col}"
            )
        )
        return boxplot
