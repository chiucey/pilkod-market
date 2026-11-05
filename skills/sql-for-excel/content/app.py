"""
Excel SQL 工作台 - Streamlit Web应用
提供Excel SQL操作的图形化界面
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

from excel_sql_processor import ExcelSQLProcessor


# 页面配置
st.set_page_config(
    page_title="Excel SQL 工作台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .table-info {
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 初始化Session State
if 'processor' not in st.session_state:
    st.session_state.processor = ExcelSQLProcessor()
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_result' not in st.session_state:
    st.session_state.last_result = None


def main():
    # 标题
    st.markdown('<p class="main-header">📊 Excel SQL 工作台</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">将Excel文件转换为SQL数据库，通过SQL语句操作数据</p>', unsafe_allow_html=True)

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📤 上传文件", "🔍 SQL查询", "📋 表信息"])

    with tab1:
        st.header("上传Excel文件")
        st.markdown("支持 .xlsx 和 .xls 格式，可以同时上传多个文件")

        uploaded_files = st.file_uploader(
            "选择Excel文件",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            help="可以同时选择多个Excel文件"
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("📥 上传文件", type="primary", use_container_width=True):
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        # 读取文件内容
                        file_bytes = uploaded_file.read()

                        # 加载到处理器
                        result = st.session_state.processor.load_excel_from_bytes(
                            file_bytes,
                            uploaded_file.name
                        )

                        if result['success']:
                            st.success(f"✅ 成功加载: {result['file_name']}")
                            for sheet in result['sheets']:
                                st.markdown(f"""
                                <div class="success-box">
                                <strong>表名:</strong> {sheet['table_name']}<br>
                                <strong>行数:</strong> {sheet['rows']} | <strong>列数:</strong> {sheet['columns']}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ 加载失败: {result['error']}")
                else:
                    st.warning("请先选择要上传的文件")

        with col2:
            # 显示已加载的表
            tables = st.session_state.processor.get_tables()
            if tables:
                st.subheader("📂 已加载的表")
                for table in tables:
                    with st.expander(f"📋 {table['table_name']}", expanded=False):
                        st.markdown(f"""
                        - **原始文件**: {table['original_file']}
                        - **Sheet名称**: {table['original_sheet']}
                        - **行数**: {table['rows']}
                        - **列数**: {table['columns']}
                        - **列名**: {', '.join(table['column_names'][:10])}{'...' if len(table['column_names']) > 10 else ''}
                        """)
                        if st.button(f"🗑️ 删除表", key=f"del_{table['table_name']}"):
                            st.session_state.processor.delete_table(table['table_name'])
                            st.rerun()
            else:
                st.info("尚未上传任何Excel文件")

        # 清除所有按钮
        if tables and st.button("🗑️ 清除所有表"):
            st.session_state.processor.clear_all()
            st.rerun()

    with tab2:
        st.header("SQL查询")

        # 显示可用表
        tables = st.session_state.processor.get_tables()
        if tables:
            with st.expander("📊 可用的表", expanded=False):
                for table in tables:
                    st.code(f"表名: {table['table_name']}", language="text")

        # SQL输入区域
        st.subheader("输入SQL语句")
        sql_input = st.text_area(
            "SQL语句",
            placeholder="示例:\nSELECT * FROM table_name WHERE column > 100\n\nINSERT INTO table_name (id, name) VALUES (1, 'Example')\n\nUPDATE table_name SET column = 'value' WHERE id = 1\n\nDELETE FROM table_name WHERE id = 1",
            height=150,
            help="支持 SELECT, INSERT, UPDATE, DELETE 语句"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            execute_btn = st.button("▶️ 执行SQL", type="primary", use_container_width=True)

        with col2:
            if st.button("📜 历史记录", use_container_width=True):
                if st.session_state.query_history:
                    st.session_state.show_history = not st.session_state.get('show_history', False)

        with col3:
            if st.button("💾 导出结果", use_container_width=True, disabled=st.session_state.last_result is None):
                if st.session_state.last_result is not None:
                    excel_data = st.session_state.processor.export_to_excel(
                        st.session_state.last_result['data']
                    )
                    st.download_button(
                        label="下载Excel",
                        data=excel_data,
                        file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        # 显示历史记录
        if st.session_state.get('show_history', False) and st.session_state.query_history:
            with st.expander("📜 查询历史", expanded=True):
                for i, hist in enumerate(reversed(st.session_state.query_history[-10:])):
                    if st.button(f"{hist['sql'][:50]}...", key=f"hist_{i}"):
                        sql_input = hist['sql']
                        st.session_state.show_history = False

        # 执行SQL
        if execute_btn and sql_input.strip():
            with st.spinner("执行中..."):
                result = st.session_state.processor.execute_sql(sql_input)

                if result['success']:
                    # 保存到历史
                    st.session_state.query_history.append({
                        'sql': sql_input,
                        'type': result['type'],
                        'timestamp': datetime.now()
                    })

                    if result['type'] == 'SELECT':
                        st.session_state.last_result = result

                        st.markdown(f"""
                        <div class="success-box">
                        ✅ 查询成功！返回 {result['row_count']} 行数据
                        </div>
                        """, unsafe_allow_html=True)

                        # 显示查询结果
                        st.dataframe(result['data'], use_container_width=True, height=400)

                        # 统计信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("返回行数", result['row_count'])
                        with col2:
                            st.metric("列数", len(result['columns']))
                        with col3:
                            st.metric("数据类型", result['data'].dtypes.value_counts().to_dict())

                    else:
                        st.markdown(f"""
                        <div class="success-box">
                        ✅ {result['type']} 操作成功！<br>
                        影响行数: {result['affected_rows']}<br>
                        表: {result.get('table', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-box">
                    ❌ 执行失败: {result['error']}
                    </div>
                    """, unsafe_allow_html=True)

        # SQL语法提示
        with st.expander("📖 SQL语法参考"):
            st.markdown("""
            ### 基本语法

            **查询数据 (SELECT)**
            ```sql
            SELECT * FROM table_name
            SELECT column1, column2 FROM table_name WHERE condition
            SELECT column, COUNT(*) as cnt FROM table_name GROUP BY column
            ```

            **插入数据 (INSERT)**
            ```sql
            INSERT INTO table_name (col1, col2) VALUES (val1, val2)
            ```

            **更新数据 (UPDATE)**
            ```sql
            UPDATE table_name SET column = value WHERE condition
            ```

            **删除数据 (DELETE)**
            ```sql
            DELETE FROM table_name WHERE condition
            ```

            **JOIN操作**
            ```sql
            SELECT a.*, b.* FROM table1 a JOIN table2 b ON a.id = b.ref_id
            ```
            """)

    with tab3:
        st.header("表信息")

        tables = st.session_state.processor.get_tables()

        if not tables:
            st.info("请先上传Excel文件")
        else:
            # 表选择器
            selected_table = st.selectbox(
                "选择要查看的表",
                options=[t['table_name'] for t in tables]
            )

            if selected_table:
                # 获取表结构
                schema = st.session_state.processor.get_table_schema(selected_table)

                if schema:
                    st.subheader(f"📋 {schema['table_name']} - 表结构")

                    # 显示列信息
                    col_df = pd.DataFrame(schema['columns'])
                    if not col_df.empty:
                        st.dataframe(col_df, use_container_width=True)

                # 显示表数据预览
                st.subheader("数据预览")
                data = st.session_state.processor.get_table_data(selected_table, limit=20)
                if data is not None:
                    st.dataframe(data, use_container_width=True)

                    st.caption(f"显示前 {min(20, len(data))} 行，共 {len(st.session_state.processor.tables[selected_table])} 行")


if __name__ == "__main__":
    main()
