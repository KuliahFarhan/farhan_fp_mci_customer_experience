import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import clickhouse_connect
import pandas as pd
from dotenv import load_dotenv


DB_NAME = "fp_mci_customer_experience"
SCRIPT_NAME = "scripts/export_dashboard_findings.py"
OUTPUT_DIR = Path("docs/query_outputs")
MARKDOWN_PATH = Path("docs/12_dashboard_query_findings.md")


@dataclass
class QuerySpec:
    name: str
    title: str
    section: str
    source: str
    sql: str
    max_rows: int = 10
    implication: str = ""


def get_clickhouse_client():
    load_dotenv()
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "password"),
        database=DB_NAME,
    )


def run_query(client, name, sql):
    try:
        return client.query_df(sql), None
    except Exception as exc:
        return pd.DataFrame(), f"{name}: {repr(exc)}"


def save_csv(name, dataframe):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{name}.csv"
    dataframe.to_csv(path, index=False)
    return path


def to_markdown_table(dataframe, max_rows=10):
    if dataframe.empty:
        return "_No rows returned._"

    df = dataframe.head(max_rows).copy()
    df.columns = [str(col) for col in df.columns]

    def fmt(value):
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            return f"{value:.2f}"
        return str(value).replace("\n", " ")

    headers = list(df.columns)
    rows = [[fmt(value) for value in row] for row in df.to_numpy()]
    widths = [
        max(len(header), *(len(row[idx]) for row in rows)) if rows else len(header)
        for idx, header in enumerate(headers)
    ]
    header_line = "| " + " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    row_lines = [
        "| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line] + row_lines)


def describe_dataframe(dataframe):
    if dataframe.empty:
        return "Query tidak mengembalikan baris sehingga belum ada pola yang dapat dibaca."

    row_count = len(dataframe)
    numeric_cols = [
        col for col in dataframe.columns
        if pd.api.types.is_numeric_dtype(dataframe[col])
    ]
    parts = [f"Hasil berisi {row_count} baris."]
    if numeric_cols:
        first_numeric = numeric_cols[0]
        parts.append(
            f"Kolom `{first_numeric}` berada pada rentang "
            f"{dataframe[first_numeric].min():.2f} sampai {dataframe[first_numeric].max():.2f}."
        )
    if row_count > 0:
        first_col = dataframe.columns[0]
        parts.append(f"Baris teratas adalah `{dataframe.iloc[0][first_col]}` berdasarkan urutan query.")
    return " ".join(parts)


def kpi_interpretation(dataframe):
    if dataframe.empty:
        return describe_dataframe(dataframe)
    row = dataframe.iloc[0].to_dict()
    return (
        f"Rata-rata review score tercatat {row.get('avg_review_score', 0):.2f}, "
        f"dengan low rating <=2 sebesar {row.get('low_rating_2_rate', 0):.2f}% dan "
        f"low rating <=3 sebesar {row.get('low_rating_3_rate', 0):.2f}%. "
        f"Late order rate berada di {row.get('late_order_rate', 0):.2f}% dari order, "
        f"sementara jumlah order yang memiliki review valid adalah {int(row.get('reviewed_orders', 0)):,}."
    )


def anomaly_interpretation(dataframe):
    if dataframe.empty:
        return describe_dataframe(dataframe)
    flagged = dataframe[dataframe["suspected_cause"] != "Normal monitoring"]
    if flagged.empty:
        return "Tidak ada bulan yang menonjol sebagai anomali besar berdasarkan aturan diagnosis konservatif."
    top = flagged.head(3)
    months = ", ".join(str(value) for value in top["review_month"].tolist())
    return (
        f"Bulan yang perlu diperiksa lebih lanjut adalah {months}. "
        "Klasifikasi ini bersifat diagnostik deskriptif dan perlu dibaca bersama konteks operasional."
    )


def write_section(lines, spec, dataframe, csv_path, interpretation):
    lines.append(f"### {spec.title}")
    lines.append("")
    lines.append(f"**Query/source table:** `{spec.source}`")
    lines.append("")
    lines.append(f"**CSV output:** `{csv_path.as_posix()}`")
    lines.append("")
    lines.append("**Key numbers and table:**")
    lines.append("")
    lines.append(to_markdown_table(dataframe, spec.max_rows))
    lines.append("")
    lines.append("**Interpretation:**")
    lines.append("")
    lines.append(interpretation)
    lines.append("")
    lines.append("**Business implication:**")
    lines.append("")
    lines.append(spec.implication or "Temuan ini digunakan sebagai sinyal prioritas analisis, bukan bukti kausal absolut.")
    lines.append("")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def q(sql):
    return sql.format(db=DB_NAME)


def build_queries():
    return [
        QuerySpec(
            "kpi_summary",
            "KPI Summary",
            "1. Executive Overview",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
                    round(countIf(review_score IS NOT NULL AND review_score <= 2) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_2_rate,
                    round(countIf(review_score IS NOT NULL AND review_score <= 3) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_3_rate,
                    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_order_rate,
                    round(avgIf(delay_days, delay_days > 0), 2) AS average_late_days,
                    countIf(review_score IS NOT NULL) AS reviewed_orders
                FROM {db}.mart_customer_experience_orders
            """),
            max_rows=5,
            implication="KPI ini memberi baseline kesehatan customer experience dan menjadi acuan untuk menilai segmen risiko.",
        ),
        QuerySpec(
            "monthly_review_trend",
            "Monthly Review Trend",
            "1. Executive Overview",
            "mart_monthly_review",
            q("""
                SELECT
                    review_month,
                    reviewed_orders,
                    round(avg_review_score, 2) AS avg_review_score,
                    low_rating_2_orders,
                    low_rating_2_rate,
                    low_rating_3_rate
                FROM {db}.mart_monthly_review
                ORDER BY review_month
            """),
            max_rows=12,
            implication="Trend bulanan membantu membedakan pola stabil dari lonjakan risiko pada periode tertentu.",
        ),
        QuerySpec(
            "review_score_distribution",
            "Review Score Distribution",
            "1. Executive Overview",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    review_score,
                    count() AS review_count,
                    round(count() * 100.0 / nullIf(sum(count()) OVER (), 0), 2) AS percentage
                FROM {db}.mart_customer_experience_orders
                WHERE review_score IS NOT NULL
                GROUP BY review_score
                ORDER BY review_score
            """),
            max_rows=10,
            implication="Distribusi skor menunjukkan apakah stagnasi rating berasal dari dominasi skor netral/rendah atau campuran skor ekstrem.",
        ),
        QuerySpec(
            "delivery_status_impact",
            "Delivery Status Impact",
            "1. Executive Overview",
            "mart_delivery_performance",
            q("""
                WITH status_summary AS (
                    SELECT
                        delivery_status,
                        sum(order_count) AS order_count,
                        round(avg(avg_review_score), 2) AS avg_review_score,
                        sum(low_rating_2_orders) AS low_rating_2_orders,
                        round(avg(avg_delivery_days), 2) AS avg_delivery_days,
                        round(avg(avg_delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_delivery_performance
                    GROUP BY delivery_status
                )
                SELECT
                    delivery_status,
                    order_count,
                    avg_review_score,
                    low_rating_2_orders,
                    round(low_rating_2_orders * 100.0 / nullIf(order_count, 0), 2) AS low_rating_2_rate,
                    avg_delivery_days,
                    avg_delay_days
                FROM status_summary
                ORDER BY low_rating_2_rate DESC, order_count DESC
            """),
            implication="Perbandingan status delivery membantu menilai apakah keterlambatan berkaitan dengan rating rendah.",
        ),
        QuerySpec(
            "delay_bucket_impact",
            "Delay Bucket Impact",
            "1. Executive Overview",
            "mart_delivery_performance",
            q("""
                WITH delay_summary AS (
                    SELECT
                        delay_bucket,
                        sum(order_count) AS order_count,
                        round(avg(avg_review_score), 2) AS avg_review_score,
                        sum(low_rating_2_orders) AS low_rating_2_orders,
                        round(avg(avg_delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_delivery_performance
                    GROUP BY delay_bucket
                )
                SELECT
                    delay_bucket,
                    order_count,
                    avg_review_score,
                    low_rating_2_orders,
                    round(low_rating_2_orders * 100.0 / nullIf(order_count, 0), 2) AS low_rating_2_rate,
                    avg_delay_days
                FROM delay_summary
                ORDER BY multiIf(
                    delay_bucket = 'early_or_on_time', 1,
                    delay_bucket = 'late_1_3_days', 2,
                    delay_bucket = 'late_4_7_days', 3,
                    delay_bucket = 'late_8_14_days', 4,
                    delay_bucket = 'late_15plus_days', 5,
                    6
                )
            """),
            implication="Bucket delay memudahkan identifikasi ambang keterlambatan yang mulai berkaitan dengan pengalaman buruk.",
        ),
        QuerySpec(
            "priority_cx_segments",
            "Priority CX Segments",
            "1. Executive Overview",
            "mart_customer_experience_items, mart_customer_experience_orders",
            q("""
                WITH segment_summary AS (
                    SELECT 'seller' AS segment_type, seller_id AS segment_name, uniqExact(order_id) AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
                           round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                           round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                           round(avg(delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                    GROUP BY seller_id
                    HAVING order_count >= 30
                    UNION ALL
                    SELECT 'product_category' AS segment_type, coalesce(product_category_name_english, product_category_name, 'unknown') AS segment_name,
                           uniqExact(order_id) AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
                           round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                           round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                           round(avg(delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                    GROUP BY segment_name
                    HAVING order_count >= 50
                    UNION ALL
                    SELECT 'customer_state' AS segment_type, customer_state AS segment_name, count() AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           sum(is_low_rating_2) AS low_rating_2_count,
                           round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                           round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                           round(avg(delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_customer_experience_orders
                    WHERE review_score IS NOT NULL
                    GROUP BY customer_state
                    HAVING order_count >= 100
                )
                SELECT
                    segment_type, segment_name, order_count, avg_review_score,
                    low_rating_2_count, low_rating_2_rate, late_rate, avg_delay_days,
                    round(sqrt(low_rating_2_count) * 5 + low_rating_2_rate * 10 + late_rate * 5, 2) AS priority_score
                FROM segment_summary
                ORDER BY priority_score DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Ranking ini membantu memilih segmen investigasi yang mempertimbangkan volume dampak dan intensitas risiko.",
        ),
        QuerySpec(
            "monthly_late_vs_low_rating",
            "Monthly Late Rate vs Low Rating",
            "2. Delivery & Fulfillment Deep Dive",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    review_month,
                    count() AS reviewed_orders,
                    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                    round(avg(delay_days), 2) AS avg_delay_days
                FROM {db}.mart_customer_experience_orders
                WHERE review_score IS NOT NULL
                  AND review_month IS NOT NULL
                GROUP BY review_month
                ORDER BY review_month
            """),
            max_rows=12,
            implication="Membandingkan late rate dan low-rating rate bulanan membantu melihat apakah shock operasional muncul bersamaan dengan penurunan review.",
        ),
        QuerySpec(
            "non_delivered_orders_by_status",
            "Non-delivered Orders by Status",
            "2. Delivery & Fulfillment Deep Dive",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    order_status,
                    count() AS order_count,
                    round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
                    countIf(review_score = 1) AS score_1_count,
                    round(countIf(review_score = 1) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS score_1_rate,
                    countIf(review_score <= 2 AND review_score IS NOT NULL) AS low_rating_1_2_count,
                    round(countIf(review_score <= 2 AND review_score IS NOT NULL) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_1_2_rate
                FROM {db}.mart_customer_experience_orders
                WHERE order_status != 'delivered'
                GROUP BY order_status
                ORDER BY order_count DESC
            """),
            implication="Status non-delivered mengindikasikan potensi friksi fulfilment yang dapat berkaitan dengan rating sangat rendah.",
        ),
        QuerySpec(
            "delivery_phase_breakdown",
            "Delivery Phase Breakdown",
            "2. Delivery & Fulfillment Deep Dive",
            "stg_orders",
            q("""
                SELECT phase, median_days, avg_days
                FROM (
                    SELECT 'approval' AS phase,
                           round(medianOrNull(dateDiff('hour', order_purchase_timestamp, order_approved_at)) / 24.0, 2) AS median_days,
                           round(avgOrNull(dateDiff('hour', order_purchase_timestamp, order_approved_at)) / 24.0, 2) AS avg_days
                    FROM {db}.stg_orders
                    WHERE order_purchase_timestamp IS NOT NULL AND order_approved_at IS NOT NULL
                    UNION ALL
                    SELECT 'seller_processing' AS phase,
                           round(medianOrNull(dateDiff('hour', order_approved_at, order_delivered_carrier_date)) / 24.0, 2) AS median_days,
                           round(avgOrNull(dateDiff('hour', order_approved_at, order_delivered_carrier_date)) / 24.0, 2) AS avg_days
                    FROM {db}.stg_orders
                    WHERE order_approved_at IS NOT NULL AND order_delivered_carrier_date IS NOT NULL
                    UNION ALL
                    SELECT 'transit' AS phase,
                           round(medianOrNull(dateDiff('hour', order_delivered_carrier_date, order_delivered_customer_date)) / 24.0, 2) AS median_days,
                           round(avgOrNull(dateDiff('hour', order_delivered_carrier_date, order_delivered_customer_date)) / 24.0, 2) AS avg_days
                    FROM {db}.stg_orders
                    WHERE order_delivered_carrier_date IS NOT NULL AND order_delivered_customer_date IS NOT NULL
                )
                ORDER BY multiIf(phase = 'approval', 1, phase = 'seller_processing', 2, phase = 'transit', 3, 4)
            """),
            implication="Breakdown fase delivery membantu memisahkan masalah approval, seller processing, dan transit.",
        ),
        QuerySpec(
            "seller_processing_time_bucket",
            "Seller Processing Time Bucket",
            "2. Delivery & Fulfillment Deep Dive",
            "stg_orders, mart_customer_experience_orders",
            q("""
                WITH base AS (
                    SELECT m.order_id, m.review_score,
                           dateDiff('day', o.order_approved_at, o.order_delivered_carrier_date) AS processing_days
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN {db}.stg_orders o ON m.order_id = o.order_id
                    WHERE m.review_score IS NOT NULL
                      AND o.order_approved_at IS NOT NULL
                      AND o.order_delivered_carrier_date IS NOT NULL
                )
                SELECT
                    multiIf(processing_days < 1, '<1d', processing_days < 2, '1-2d', processing_days < 3, '2-3d', processing_days < 7, '3-7d', '7d+') AS processing_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
                    round(avg(processing_days), 2) AS avg_processing_days
                FROM base
                GROUP BY processing_bucket
                ORDER BY multiIf(processing_bucket = '<1d', 1, processing_bucket = '1-2d', 2, processing_bucket = '2-3d', 3, processing_bucket = '3-7d', 4, processing_bucket = '7d+', 5, 6)
            """),
            implication="Bucket processing menunjukkan apakah waktu seller sebelum pickup berkaitan dengan risiko review.",
        ),
        QuerySpec(
            "transit_time_bucket",
            "Transit Time Bucket",
            "2. Delivery & Fulfillment Deep Dive",
            "stg_orders, mart_customer_experience_orders",
            q("""
                WITH base AS (
                    SELECT m.order_id, m.review_score,
                           dateDiff('day', o.order_delivered_carrier_date, o.order_delivered_customer_date) AS transit_days
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN {db}.stg_orders o ON m.order_id = o.order_id
                    WHERE m.review_score IS NOT NULL
                      AND o.order_delivered_carrier_date IS NOT NULL
                      AND o.order_delivered_customer_date IS NOT NULL
                )
                SELECT
                    multiIf(transit_days < 3, '<3d', transit_days < 5, '3-5d', transit_days < 7, '5-7d', transit_days < 10, '7-10d', '>10d') AS transit_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
                    round(avg(transit_days), 2) AS avg_transit_days
                FROM base
                GROUP BY transit_bucket
                ORDER BY multiIf(transit_bucket = '<3d', 1, transit_bucket = '3-5d', 2, transit_bucket = '5-7d', 3, transit_bucket = '7-10d', 4, transit_bucket = '>10d', 5, 6)
            """),
            implication="Transit bucket memberi sinyal apakah durasi carrier berkaitan dengan customer dissatisfaction.",
        ),
        QuerySpec(
            "delivery_performance_matrix",
            "Delivery Performance Matrix",
            "2. Delivery & Fulfillment Deep Dive",
            "mart_delivery_performance",
            q("""
                SELECT
                    delivery_status,
                    delay_bucket,
                    order_count,
                    round(avg_review_score, 2) AS avg_review_score,
                    low_rating_2_orders,
                    round(low_rating_2_orders * 100.0 / nullIf(order_count, 0), 2) AS low_rating_2_rate,
                    round(avg_delivery_days, 2) AS avg_delivery_days,
                    round(avg_delay_days, 2) AS avg_delay_days
                FROM {db}.mart_delivery_performance
                ORDER BY delivery_status, delay_bucket
            """),
            implication="Matrix ini menghubungkan status delivery dan delay bucket pada satu tampilan operasional.",
        ),
        QuerySpec(
            "seller_delivery_risk_label",
            "Seller Delivery Risk Label",
            "2. Delivery & Fulfillment Deep Dive",
            "mart_customer_experience_items",
            q("""
                WITH seller_summary AS (
                    SELECT seller_id, seller_city, seller_state,
                           uniqExact(order_id) AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                           round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                           round(avg(delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                    GROUP BY seller_id, seller_city, seller_state
                    HAVING order_count >= 30
                )
                SELECT *,
                    multiIf(low_rating_2_rate >= 25 AND late_rate >= 15, 'High risk seller',
                            late_rate >= 15, 'Delivery issue seller',
                            low_rating_2_rate >= 25, 'Review issue seller', 'Monitor') AS risk_label
                FROM seller_summary
                ORDER BY low_rating_2_rate DESC, late_rate DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Risk label seller membantu memisahkan seller dengan isu delivery, review, atau kombinasi keduanya.",
        ),
        QuerySpec(
            "category_delivery_risk_label",
            "Category Delivery Risk Label",
            "2. Delivery & Fulfillment Deep Dive",
            "mart_customer_experience_items",
            q("""
                WITH category_summary AS (
                    SELECT coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
                           uniqExact(order_id) AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                           round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                           round(avg(delay_days), 2) AS avg_delay_days
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                    GROUP BY product_category
                    HAVING order_count >= 50
                )
                SELECT *,
                    multiIf(low_rating_2_rate >= 25 AND late_rate >= 15, 'High risk category',
                            late_rate >= 15, 'Delivery issue category',
                            low_rating_2_rate >= 25, 'Review issue category', 'Monitor') AS risk_label
                FROM category_summary
                ORDER BY low_rating_2_rate DESC, late_rate DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Risk label category mengarahkan audit kategori produk yang berkaitan dengan pengalaman buruk.",
        ),
        QuerySpec(
            "top_risk_sellers",
            "Top Risk Sellers by Low Rating Contribution",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_items",
            q("""
                WITH total_low_rating AS (
                    SELECT uniqExactIf(order_id, review_score <= 2) AS total_low_rating_2_orders
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                )
                SELECT
                    seller_id, seller_city, seller_state,
                    uniqExact(order_id) AS order_count,
                    count() AS item_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
                    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(any(total_low_rating_2_orders), 0), 2) AS low_rating_contribution_score
                FROM {db}.mart_customer_experience_items
                CROSS JOIN total_low_rating
                WHERE review_score IS NOT NULL
                GROUP BY seller_id, seller_city, seller_state
                HAVING order_count >= 30
                ORDER BY low_rating_2_count DESC, low_rating_2_rate DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Seller dengan kontribusi low-rating tinggi menjadi kandidat monitoring dan coaching prioritas.",
        ),
        QuerySpec(
            "seller_risk_quadrant",
            "Seller Risk Quadrant",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_items",
            q("""
                WITH seller_summary AS (
                    SELECT seller_id, seller_state, uniqExact(order_id) AS order_count,
                           round(avg(review_score), 2) AS avg_review_score,
                           round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_2_rate
                    FROM {db}.mart_customer_experience_items
                    WHERE review_score IS NOT NULL
                    GROUP BY seller_id, seller_state
                    HAVING order_count >= 50
                ), thresholds AS (
                    SELECT quantileExact(0.5)(order_count) AS median_order_count,
                           quantileExact(0.5)(avg_review_score) AS median_review_score
                    FROM seller_summary
                )
                SELECT s.*,
                    multiIf(s.order_count >= t.median_order_count AND s.avg_review_score >= t.median_review_score, 'Stars',
                            s.order_count >= t.median_order_count AND s.avg_review_score < t.median_review_score, 'Risk zone',
                            s.order_count < t.median_order_count AND s.avg_review_score >= t.median_review_score, 'Sleepers',
                            'Problematic') AS seller_quadrant
                FROM seller_summary s
                CROSS JOIN thresholds t
                ORDER BY order_count DESC, avg_review_score ASC
                LIMIT 50
            """),
            max_rows=15,
            implication="Quadrant seller mendukung segmentasi action plan berdasarkan volume dan rating.",
        ),
        QuerySpec(
            "top_risk_categories",
            "Top Risk Categories by Low Rating Contribution",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_items",
            q("""
                SELECT
                    coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
                    uniqExact(order_id) AS order_count,
                    count() AS item_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
                    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                    uniqExactIf(order_id, delivery_status = 'late') AS late_order_count,
                    round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate
                FROM {db}.mart_customer_experience_items
                WHERE review_score IS NOT NULL
                GROUP BY product_category
                HAVING order_count >= 50
                ORDER BY low_rating_2_count DESC, low_rating_2_rate DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Kategori berisiko dapat diarahkan ke audit kualitas, packaging, dan ekspektasi pelanggan.",
        ),
        QuerySpec(
            "category_performance_matrix",
            "Category Performance Matrix",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_items",
            q("""
                SELECT
                    coalesce(product_category_name_english, product_category_name, 'unknown') AS product_category,
                    uniqExact(order_id) AS order_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_2_rate,
                    round(uniqExactIf(order_id, review_score <= 3) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_1_3_rate
                FROM {db}.mart_customer_experience_items
                WHERE review_score IS NOT NULL
                GROUP BY product_category
                HAVING order_count >= 50
                ORDER BY order_count DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Matrix category memisahkan kategori besar yang stabil dari kategori yang memerlukan mitigasi CX.",
        ),
        QuerySpec(
            "customer_region_risk",
            "Customer Region Risk",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    customer_state,
                    count() AS order_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    sum(is_low_rating_2) AS low_rating_2_count,
                    round(sum(is_low_rating_2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                    countIf(delivery_status = 'late') AS late_orders,
                    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(avg(delay_days), 2) AS avg_delay_days
                FROM {db}.mart_customer_experience_orders
                WHERE review_score IS NOT NULL
                GROUP BY customer_state
                HAVING order_count >= 100
                ORDER BY low_rating_2_rate DESC, late_rate DESC
            """),
            max_rows=15,
            implication="Region pelanggan membantu mengidentifikasi area pengalaman yang konsisten lebih berisiko.",
        ),
        QuerySpec(
            "seller_region_risk",
            "Seller Region Risk",
            "3. Segment Risk: Seller, Category, Region",
            "mart_customer_experience_items",
            q("""
                SELECT
                    seller_state,
                    uniqExact(order_id) AS order_count,
                    count() AS item_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    uniqExactIf(order_id, review_score <= 2) AS low_rating_2_count,
                    round(uniqExactIf(order_id, review_score <= 2) * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS low_rating_2_rate,
                    uniqExactIf(order_id, delivery_status = 'late') AS late_order_count,
                    round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                    round(avg(delay_days), 2) AS avg_delay_days
                FROM {db}.mart_customer_experience_items
                WHERE review_score IS NOT NULL
                GROUP BY seller_state
                HAVING order_count >= 100
                ORDER BY low_rating_2_rate DESC, order_count DESC
            """),
            max_rows=15,
            implication="Seller region risk memberi sinyal wilayah seller yang memerlukan monitoring operasional.",
        ),
        QuerySpec(
            "customer_retention_funnel",
            "Customer Retention Funnel",
            "4. Customer & Order Behavior",
            "stg_orders, stg_customers",
            q("""
                WITH customer_orders AS (
                    SELECT c.customer_unique_id, count() AS total_orders
                    FROM {db}.stg_orders o
                    LEFT JOIN {db}.stg_customers c ON o.customer_id = c.customer_id
                    GROUP BY c.customer_unique_id
                ), bucketed AS (
                    SELECT customer_unique_id,
                           multiIf(total_orders = 1, '1 order', total_orders = 2, '2 orders', '3+ orders') AS retention_bucket
                    FROM customer_orders
                )
                SELECT
                    retention_bucket,
                    count() AS customer_count,
                    round(count() * 100.0 / nullIf(sum(count()) OVER (), 0), 2) AS customer_share
                FROM bucketed
                GROUP BY retention_bucket
                ORDER BY multiIf(retention_bucket = '1 order', 1, retention_bucket = '2 orders', 2, retention_bucket = '3+ orders', 3, 4)
            """),
            implication="Retention funnel menunjukkan struktur pembelian ulang yang menjadi konteks customer experience.",
        ),
        QuerySpec(
            "multi_seller_order_effect",
            "Multi-seller Order Effect",
            "4. Customer & Order Behavior",
            "stg_order_items, mart_customer_experience_orders",
            q("""
                WITH order_seller_counts AS (
                    SELECT order_id, uniqExact(seller_id) AS seller_count
                    FROM {db}.stg_order_items
                    GROUP BY order_id
                ), base AS (
                    SELECT m.order_id, m.review_score, m.delivery_days, s.seller_count
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN order_seller_counts s ON m.order_id = s.order_id
                    WHERE m.review_score IS NOT NULL
                )
                SELECT
                    multiIf(seller_count = 1, '1 seller', seller_count = 2, '2 sellers', seller_count = 3, '3 sellers', '4+ sellers') AS seller_count_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
                    round(avg(delivery_days), 2) AS avg_delivery_days
                FROM base
                GROUP BY seller_count_bucket
                ORDER BY multiIf(seller_count_bucket = '1 seller', 1, seller_count_bucket = '2 sellers', 2, seller_count_bucket = '3 sellers', 3, seller_count_bucket = '4+ sellers', 4, 5)
            """),
            implication="Multi-seller bucket menguji apakah kompleksitas fulfilment berkaitan dengan rating dan delivery days.",
        ),
        QuerySpec(
            "item_count_effect",
            "Item Count Effect",
            "4. Customer & Order Behavior",
            "stg_order_items, mart_customer_experience_orders",
            q("""
                WITH order_item_counts AS (
                    SELECT order_id, count() AS item_count
                    FROM {db}.stg_order_items
                    GROUP BY order_id
                ), base AS (
                    SELECT m.order_id, m.review_score, i.item_count
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN order_item_counts i ON m.order_id = i.order_id
                    WHERE m.review_score IS NOT NULL
                )
                SELECT
                    multiIf(item_count = 1, '1 item', item_count = 2, '2 items', item_count = 3, '3 items', '4+ items') AS item_count_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate
                FROM base
                GROUP BY item_count_bucket
                ORDER BY multiIf(item_count_bucket = '1 item', 1, item_count_bucket = '2 items', 2, item_count_bucket = '3 items', 3, item_count_bucket = '4+ items', 4, 5)
            """),
            implication="Item count membantu membaca apakah kompleksitas order berkaitan dengan customer dissatisfaction.",
        ),
        QuerySpec(
            "order_value_bucket_risk",
            "Order Value Bucket Risk",
            "4. Customer & Order Behavior",
            "stg_order_payments, mart_customer_experience_orders",
            q("""
                WITH order_value AS (
                    SELECT order_id, sum(payment_value) AS total_order_value
                    FROM {db}.stg_order_payments
                    GROUP BY order_id
                ), base AS (
                    SELECT m.order_id, m.review_score, v.total_order_value
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN order_value v ON m.order_id = v.order_id
                    WHERE m.review_score IS NOT NULL
                )
                SELECT
                    multiIf(total_order_value < 50, '<50', total_order_value < 100, '50-100', total_order_value < 200, '100-200', total_order_value < 500, '200-500', '500+') AS order_value_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
                    round(avg(total_order_value), 2) AS avg_order_value
                FROM base
                GROUP BY order_value_bucket
                ORDER BY multiIf(order_value_bucket = '<50', 1, order_value_bucket = '50-100', 2, order_value_bucket = '100-200', 3, order_value_bucket = '200-500', 4, order_value_bucket = '500+', 5, 6)
            """),
            implication="Order value bucket membantu melihat apakah nilai transaksi berkaitan dengan risiko rating.",
        ),
        QuerySpec(
            "installment_vs_review",
            "Installment vs Review Score",
            "4. Customer & Order Behavior",
            "stg_order_payments, mart_customer_experience_orders",
            q("""
                WITH payment_base AS (
                    SELECT order_id,
                           maxIf(payment_installments, payment_type = 'credit_card') AS cc_installments,
                           sumIf(payment_value, payment_type = 'credit_card') AS cc_payment_value
                    FROM {db}.stg_order_payments
                    GROUP BY order_id
                ), base AS (
                    SELECT m.order_id, m.review_score, p.cc_installments, p.cc_payment_value
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN payment_base p ON m.order_id = p.order_id
                    WHERE m.review_score IS NOT NULL AND p.cc_installments > 0
                )
                SELECT
                    multiIf(cc_installments = 1, '1x', cc_installments BETWEEN 2 AND 3, '2-3x', cc_installments BETWEEN 4 AND 6, '4-6x', cc_installments BETWEEN 7 AND 12, '7-12x', '13-24x') AS installment_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(avg(cc_payment_value), 2) AS avg_order_value
                FROM base
                GROUP BY installment_bucket
                ORDER BY multiIf(installment_bucket = '1x', 1, installment_bucket = '2-3x', 2, installment_bucket = '4-6x', 3, installment_bucket = '7-12x', 4, installment_bucket = '13-24x', 5, 6)
            """),
            implication="Installment bucket dapat menjadi indikator perilaku pembayaran dan ekspektasi order value.",
        ),
        QuerySpec(
            "review_timing_after_answer",
            "Review Timing After Delivery",
            "4. Customer & Order Behavior",
            "stg_order_reviews, mart_customer_experience_orders",
            q("""
                WITH latest_reviews AS (
                    SELECT *
                    FROM (
                        SELECT *,
                               row_number() OVER (PARTITION BY order_id ORDER BY review_answer_timestamp DESC, review_creation_date DESC) AS rn
                        FROM {db}.stg_order_reviews
                    )
                    WHERE rn = 1
                ), base AS (
                    SELECT
                        m.order_id,
                        m.review_score,
                        dateDiff('day', m.order_delivered_customer_date, r.review_answer_timestamp) AS review_answer_lag_days
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN latest_reviews r ON m.order_id = r.order_id
                    WHERE m.review_score IS NOT NULL
                      AND r.review_answer_timestamp IS NOT NULL
                      AND m.order_delivered_customer_date IS NOT NULL
                      AND r.review_answer_timestamp >= m.order_delivered_customer_date
                )
                SELECT
                    multiIf(review_answer_lag_days = 0, 'same day', review_answer_lag_days = 1, '1 day', review_answer_lag_days BETWEEN 2 AND 7, '2-7 days', review_answer_lag_days BETWEEN 8 AND 14, '8-14 days', '15+ days') AS review_answer_timing_bucket,
                    count() AS review_count,
                    round(avg(review_score), 2) AS avg_review_score
                FROM base
                GROUP BY review_answer_timing_bucket
                ORDER BY multiIf(review_answer_timing_bucket = 'same day', 1, review_answer_timing_bucket = '1 day', 2, review_answer_timing_bucket = '2-7 days', 3, review_answer_timing_bucket = '8-14 days', 4, review_answer_timing_bucket = '15+ days', 5, 6)
            """),
            implication="Timing berbasis `review_answer_timestamp` membantu membaca kapan feedback diproses setelah delivery.",
        ),
        QuerySpec(
            "order_complexity_risk_matrix",
            "Order Complexity Risk Matrix",
            "4. Customer & Order Behavior",
            "stg_order_items, mart_customer_experience_orders",
            q("""
                WITH order_complexity AS (
                    SELECT order_id, count() AS item_count, uniqExact(seller_id) AS seller_count
                    FROM {db}.stg_order_items
                    GROUP BY order_id
                ), base AS (
                    SELECT
                        m.order_id,
                        m.review_score,
                        m.delivery_days,
                        c.item_count,
                        c.seller_count
                    FROM {db}.mart_customer_experience_orders m
                    INNER JOIN order_complexity c ON m.order_id = c.order_id
                    WHERE m.review_score IS NOT NULL
                )
                SELECT
                    multiIf(item_count = 1, '1 item', item_count = 2, '2 items', item_count = 3, '3 items', '4+ items') AS item_count_bucket,
                    multiIf(seller_count = 1, '1 seller', seller_count = 2, '2 sellers', seller_count = 3, '3 sellers', '4+ sellers') AS seller_count_bucket,
                    count() AS reviewed_orders,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_1_2_rate,
                    round(avg(delivery_days), 2) AS avg_delivery_days
                FROM base
                GROUP BY item_count_bucket, seller_count_bucket
                ORDER BY low_rating_1_2_rate DESC, reviewed_orders DESC
            """),
            max_rows=15,
            implication="Matrix kompleksitas order menggabungkan jumlah item dan seller untuk membaca potensi friksi fulfilment.",
        ),
        QuerySpec(
            "customer_state_late_hotspot",
            "Customer State Late Hotspot",
            "5. Geolocation & Spatial Risk",
            "mart_customer_experience_orders",
            q("""
                SELECT
                    customer_state,
                    count() AS order_count,
                    countIf(delivery_status = 'late') AS late_orders,
                    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(avg(delivery_days), 2) AS avg_delivery_days,
                    round(avg(review_score), 2) AS avg_review_score
                FROM {db}.mart_customer_experience_orders
                WHERE customer_state IS NOT NULL
                GROUP BY customer_state
                HAVING order_count >= 100
                ORDER BY late_rate DESC, order_count DESC
            """),
            max_rows=15,
            implication="Hotspot late rate per state membantu menentukan wilayah tujuan yang perlu ditelusuri lebih lanjut.",
        ),
        QuerySpec(
            "problem_routes",
            "Problem Routes Flow/Ranking",
            "5. Geolocation & Spatial Risk",
            "mart_customer_experience_items",
            q("""
                SELECT
                    concat(seller_state, ' -> ', customer_state) AS route,
                    seller_state,
                    customer_state,
                    uniqExact(order_id) AS order_count,
                    round(uniqExactIf(order_id, delivery_status = 'late') * 100.0 / nullIf(uniqExact(order_id), 0), 2) AS late_rate,
                    round(avg(review_score), 2) AS avg_review_score,
                    round(avg(delivery_days), 2) AS avg_delivery_days
                FROM {db}.mart_customer_experience_items
                WHERE review_score IS NOT NULL
                  AND seller_state IS NOT NULL
                  AND customer_state IS NOT NULL
                GROUP BY seller_state, customer_state
                HAVING order_count >= 100
                ORDER BY late_rate DESC, order_count DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="Route ranking menunjukkan pasangan wilayah seller-customer yang berkaitan dengan risiko delivery.",
        ),
        QuerySpec(
            "distance_bucket_late_rate",
            "Distance Bucket vs Late Rate",
            "5. Geolocation & Spatial Risk",
            "geo_zip_prefix_reference, stg_customers, stg_sellers, stg_order_items, mart_customer_experience_orders",
            q("""
                WITH single_seller_orders AS (
                    SELECT DISTINCT order_id, seller_id
                    FROM {db}.stg_order_items
                    WHERE order_id IN (
                        SELECT order_id
                        FROM {db}.stg_order_items
                        GROUP BY order_id
                        HAVING uniqExact(seller_id) = 1
                    )
                ), order_distance AS (
                    SELECT
                        o.delivery_status,
                        o.delivery_days,
                        o.delay_days,
                        greatCircleDistance(seller_geo.representative_lng, seller_geo.representative_lat, customer_geo.representative_lng, customer_geo.representative_lat) / 1000.0 AS distance_km
                    FROM {db}.mart_customer_experience_orders AS o
                    INNER JOIN {db}.stg_customers AS c ON o.customer_id = c.customer_id
                    INNER JOIN single_seller_orders AS ss ON o.order_id = ss.order_id
                    INNER JOIN {db}.stg_sellers AS s ON ss.seller_id = s.seller_id
                    INNER JOIN {db}.geo_zip_prefix_reference AS customer_geo ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
                    INNER JOIN {db}.geo_zip_prefix_reference AS seller_geo ON s.seller_zip_code_prefix = seller_geo.geolocation_zip_code_prefix
                    WHERE o.order_delivered_customer_date IS NOT NULL
                ), bucketed AS (
                    SELECT
                        delivery_status,
                        delivery_days,
                        delay_days,
                        multiIf(distance_km < 50, '<50 km', distance_km < 100, '50-100 km', distance_km < 250, '100-250 km', distance_km < 500, '250-500 km', distance_km < 1000, '500-1000 km', '>1000 km') AS distance_bucket
                    FROM order_distance
                )
                SELECT
                    distance_bucket,
                    count() AS order_count,
                    countIf(delivery_status = 'late') AS late_order_count,
                    round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(avg(delivery_days), 2) AS avg_delivery_days,
                    round(avg(delay_days), 2) AS avg_delay_days
                FROM bucketed
                GROUP BY distance_bucket
                ORDER BY multiIf(distance_bucket = '<50 km', 1, distance_bucket = '50-100 km', 2, distance_bucket = '100-250 km', 3, distance_bucket = '250-500 km', 4, distance_bucket = '500-1000 km', 5, 6)
            """),
            implication="Distance bucket memperlihatkan apakah jarak seller-customer berkaitan dengan keterlambatan.",
        ),
        QuerySpec(
            "distance_bucket_low_rating_rate",
            "Distance Bucket vs Low-Rating Rate",
            "5. Geolocation & Spatial Risk",
            "geo_zip_prefix_reference, stg_customers, stg_sellers, stg_order_items, mart_customer_experience_orders",
            q("""
                WITH single_seller_orders AS (
                    SELECT DISTINCT order_id, seller_id
                    FROM {db}.stg_order_items
                    WHERE order_id IN (
                        SELECT order_id
                        FROM {db}.stg_order_items
                        GROUP BY order_id
                        HAVING uniqExact(seller_id) = 1
                    )
                ), order_distance AS (
                    SELECT
                        o.review_score,
                        greatCircleDistance(seller_geo.representative_lng, seller_geo.representative_lat, customer_geo.representative_lng, customer_geo.representative_lat) / 1000.0 AS distance_km
                    FROM {db}.mart_customer_experience_orders AS o
                    INNER JOIN {db}.stg_customers AS c ON o.customer_id = c.customer_id
                    INNER JOIN single_seller_orders AS ss ON o.order_id = ss.order_id
                    INNER JOIN {db}.stg_sellers AS s ON ss.seller_id = s.seller_id
                    INNER JOIN {db}.geo_zip_prefix_reference AS customer_geo ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
                    INNER JOIN {db}.geo_zip_prefix_reference AS seller_geo ON s.seller_zip_code_prefix = seller_geo.geolocation_zip_code_prefix
                    WHERE o.review_score IS NOT NULL
                ), bucketed AS (
                    SELECT
                        review_score,
                        multiIf(distance_km < 50, '<50 km', distance_km < 100, '50-100 km', distance_km < 250, '100-250 km', distance_km < 500, '250-500 km', distance_km < 1000, '500-1000 km', '>1000 km') AS distance_bucket
                    FROM order_distance
                )
                SELECT
                    distance_bucket,
                    count() AS reviewed_order_count,
                    round(avg(review_score), 2) AS avg_review_score,
                    countIf(review_score <= 2) AS low_rating_2_count,
                    round(countIf(review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                    countIf(review_score <= 3) AS low_rating_3_count,
                    round(countIf(review_score <= 3) * 100.0 / nullIf(count(), 0), 2) AS low_rating_3_rate
                FROM bucketed
                GROUP BY distance_bucket
                ORDER BY multiIf(distance_bucket = '<50 km', 1, distance_bucket = '50-100 km', 2, distance_bucket = '100-250 km', 3, distance_bucket = '250-500 km', 4, distance_bucket = '500-1000 km', 5, 6)
            """),
            implication="Distance vs rating membantu membaca apakah jarak jauh juga berkaitan dengan persepsi pelanggan.",
        ),
        QuerySpec(
            "eta_deviation_destination_state",
            "ETA Deviation by Destination State",
            "5. Geolocation & Spatial Risk",
            "mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference",
            q("""
                SELECT
                    c.customer_state,
                    count() AS order_count,
                    round(avg(o.delivery_days), 2) AS avg_delivery_days,
                    round(avg(o.delay_days), 2) AS avg_delay_days,
                    countIf(o.delivery_status = 'late') AS late_order_count,
                    round(countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(avg(o.review_score), 2) AS avg_review_score
                FROM {db}.mart_customer_experience_orders AS o
                INNER JOIN {db}.stg_customers AS c ON o.customer_id = c.customer_id
                INNER JOIN {db}.geo_zip_prefix_reference AS customer_geo ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
                WHERE o.order_delivered_customer_date IS NOT NULL
                  AND o.order_estimated_delivery_date IS NOT NULL
                GROUP BY c.customer_state
                HAVING order_count >= 100
                ORDER BY avg_delay_days DESC, late_rate DESC, order_count DESC
            """),
            max_rows=15,
            implication="ETA deviation state membantu mengidentifikasi wilayah tujuan dengan estimasi delivery yang relatif kurang stabil.",
        ),
        QuerySpec(
            "worst_destination_zip_prefix_areas",
            "Worst Destination ZIP Prefix Areas",
            "5. Geolocation & Spatial Risk",
            "mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference",
            q("""
                SELECT
                    c.customer_zip_code_prefix,
                    customer_geo.representative_city,
                    customer_geo.representative_state,
                    count() AS order_count,
                    round(avg(o.review_score), 2) AS avg_review_score,
                    round(countIf(o.review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                    round(countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(avg(o.delay_days), 2) AS avg_delay_days
                FROM {db}.mart_customer_experience_orders AS o
                INNER JOIN {db}.stg_customers AS c ON o.customer_id = c.customer_id
                INNER JOIN {db}.geo_zip_prefix_reference AS customer_geo ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
                WHERE o.review_score IS NOT NULL
                GROUP BY c.customer_zip_code_prefix, customer_geo.representative_city, customer_geo.representative_state
                HAVING order_count >= 30
                ORDER BY low_rating_2_rate DESC, late_rate DESC, avg_review_score ASC, order_count DESC
                LIMIT 50
            """),
            max_rows=15,
            implication="ZIP prefix table berguna sebagai daftar area tujuan yang layak ditelusuri, dengan batas volume minimum agar tidak terlalu noisy.",
        ),
        QuerySpec(
            "destination_zip_prefix_risk_table",
            "Destination ZIP Prefix Risk Table",
            "5. Geolocation & Spatial Risk",
            "mart_customer_experience_orders, stg_customers, geo_zip_prefix_reference",
            q("""
                SELECT
                    customer_geo.representative_state,
                    customer_geo.representative_city,
                    c.customer_zip_code_prefix,
                    count() AS reviewed_orders,
                    round(avg(o.review_score), 2) AS avg_review_score,
                    round(countIf(o.review_score <= 2) * 100.0 / nullIf(count(), 0), 2) AS low_rating_2_rate,
                    round(countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                    round(sqrt(countIf(o.review_score <= 2)) * 5 + (countIf(o.review_score <= 2) * 100.0 / nullIf(count(), 0)) * 10 + (countIf(o.delivery_status = 'late') * 100.0 / nullIf(count(), 0)) * 5, 2) AS zip_risk_score
                FROM {db}.mart_customer_experience_orders AS o
                INNER JOIN {db}.stg_customers AS c ON o.customer_id = c.customer_id
                INNER JOIN {db}.geo_zip_prefix_reference AS customer_geo ON c.customer_zip_code_prefix = customer_geo.geolocation_zip_code_prefix
                WHERE o.review_score IS NOT NULL
                GROUP BY customer_geo.representative_state, customer_geo.representative_city, c.customer_zip_code_prefix
                HAVING reviewed_orders >= 30
                ORDER BY zip_risk_score DESC
                LIMIT 100
            """),
            max_rows=15,
            implication="Risk score area tujuan membantu memilih lokasi prioritas untuk investigasi delivery dan customer experience.",
        ),
        QuerySpec(
            "monthly_rating_anomaly_diagnosis",
            "Monthly Rating Anomaly Diagnosis",
            "6. Monthly Rating Anomaly Diagnosis",
            "mart_customer_experience_orders",
            q("""
                WITH monthly AS (
                    SELECT
                        review_month,
                        countIf(review_score IS NOT NULL) AS reviewed_orders,
                        round(avgIf(review_score, review_score IS NOT NULL), 2) AS avg_review_score,
                        round(countIf(review_score <= 2 AND review_score IS NOT NULL) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS low_rating_2_rate,
                        round(countIf(delivery_status = 'late') * 100.0 / nullIf(count(), 0), 2) AS late_rate,
                        round(countIf(order_status != 'delivered') * 100.0 / nullIf(count(), 0), 2) AS non_delivered_rate,
                        round(countIf(review_score = 1) * 100.0 / nullIf(countIf(review_score IS NOT NULL), 0), 2) AS score_1_rate
                    FROM {db}.mart_customer_experience_orders
                    WHERE review_month IS NOT NULL
                    GROUP BY review_month
                ), baselines AS (
                    SELECT
                        quantileExact(0.5)(reviewed_orders) AS median_reviewed_orders,
                        avg(low_rating_2_rate) AS avg_low_rating_2_rate,
                        stddevPop(low_rating_2_rate) AS std_low_rating_2_rate,
                        avg(late_rate) AS avg_late_rate,
                        stddevPop(late_rate) AS std_late_rate,
                        avg(non_delivered_rate) AS avg_non_delivered_rate,
                        stddevPop(non_delivered_rate) AS std_non_delivered_rate,
                        avg(score_1_rate) AS avg_score_1_rate,
                        stddevPop(score_1_rate) AS std_score_1_rate
                    FROM monthly
                )
                SELECT
                    review_month,
                    reviewed_orders,
                    avg_review_score,
                    low_rating_2_rate,
                    late_rate,
                    non_delivered_rate,
                    score_1_rate,
                    multiIf(
                        reviewed_orders < median_reviewed_orders * 0.25, 'Low sample / early-period instability',
                        late_rate > avg_late_rate + std_late_rate, 'Delivery delay shock',
                        non_delivered_rate > avg_non_delivered_rate + std_non_delivered_rate, 'Non-delivered order issue',
                        score_1_rate > avg_score_1_rate + std_score_1_rate OR low_rating_2_rate > avg_low_rating_2_rate + std_low_rating_2_rate, 'Customer dissatisfaction spike',
                        'Normal monitoring'
                    ) AS suspected_cause
                FROM monthly
                CROSS JOIN baselines
                ORDER BY review_month
            """),
            max_rows=24,
            implication="Diagnosis anomali bulanan membantu membedakan masalah ukuran sampel dari pola operasional yang perlu ditelusuri.",
        ),
    ]


def build_markdown(results, warnings, generated_at):
    lines = [
        "# Dashboard Query Findings - Customer Experience Root Cause Analysis",
        "",
        f"Generated at: `{generated_at}`",
        f"ClickHouse database: `{DB_NAME}`",
        f"Script: `{SCRIPT_NAME}`",
        "",
        "Note: hasil angka bergantung pada kondisi data mart saat script dijalankan.",
        "",
        "## Query execution warnings",
        "",
    ]

    if warnings:
        lines.extend([f"- {warning}" for warning in warnings])
    else:
        lines.append("- Tidak ada query warning.")
    lines.append("")

    sections = [
        "1. Executive Overview",
        "2. Delivery & Fulfillment Deep Dive",
        "3. Segment Risk: Seller, Category, Region",
        "4. Customer & Order Behavior",
        "5. Geolocation & Spatial Risk",
        "6. Monthly Rating Anomaly Diagnosis",
    ]

    for section in sections:
        lines.append(f"## {section}")
        lines.append("")
        for spec, dataframe, csv_path in results:
            if spec.section != section:
                continue
            if spec.name == "kpi_summary":
                interpretation = kpi_interpretation(dataframe)
            elif spec.name == "monthly_rating_anomaly_diagnosis":
                interpretation = anomaly_interpretation(dataframe)
            else:
                interpretation = describe_dataframe(dataframe)
            write_section(lines, spec, dataframe, csv_path, interpretation)

    lines.extend([
        "## 7. Overall Root Cause Summary",
        "",
        "- Bukti deskriptif menunjukkan bahwa keterlambatan delivery berkaitan dengan review score yang lebih rendah dan low-rating rate yang lebih tinggi.",
        "- Risiko customer experience tidak hanya muncul dari delivery delay. Seller, kategori produk, wilayah pelanggan, kompleksitas order, dan jarak geografi juga menunjukkan pola risiko yang perlu dimonitor.",
        "- Temuan ini tidak menyatakan hubungan kausal absolut. Angka-angka mendukung interpretasi bahwa beberapa faktor operasional dan segmentasi berkaitan dengan pengalaman pelanggan yang lebih buruk.",
        "- Rekomendasi CEO: prioritaskan monitoring seller dan kategori berisiko tinggi, perbaiki SLA untuk route/wilayah bermasalah, audit area ZIP prefix dengan low-rating rate tinggi, dan pantau anomali bulanan sebagai early warning.",
        "- Untuk eksekusi bisnis, gunakan dashboard sebagai triage, lalu validasi tindakan dengan drill-down order, seller operation review, dan follow-up customer feedback.",
        "",
    ])

    return "\n".join(lines)


def main():
    generated_at = datetime.now().isoformat(timespec="seconds")
    client = get_clickhouse_client()
    warnings = []
    results = []

    try:
        for spec in build_queries():
            dataframe, warning = run_query(client, spec.name, spec.sql)
            if warning:
                warnings.append(warning)
            csv_path = save_csv(slug(spec.name), dataframe)
            results.append((spec, dataframe, csv_path))
    finally:
        client.close()

    MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text(
        build_markdown(results, warnings, generated_at),
        encoding="utf-8",
    )

    print(f"Generated Markdown: {MARKDOWN_PATH}")
    print(f"CSV output directory: {OUTPUT_DIR}")
    print(f"Queries succeeded: {len(results) - len(warnings)}")
    print(f"Queries failed: {len(warnings)}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
