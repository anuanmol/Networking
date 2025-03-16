import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import psutil
import streamlit as st

def main():
    st.title("Network Dashboard")

    st.write("This is a simple network dashboard which can show basic network commands results like ipconfig, ping, tracert, etc.")
    command = st.text_input("Enter the command:")
    if st.button("Run"):
        result = os.popen(command).read()
        st.text_area("Command Output", result, height=300)

    st.write("---")
    st.write("")
    
    # Placeholder for the first chart
    with st.container():
        st.write("##### Latency")
        latency_placeholder = st.empty()

    # Create columns for the second row of charts
    col1, col2 = st.columns(2)

    # Placeholders for the second row of charts
    with col1.container():
        st.write("##### Bandwidth")
        bandwidth_placeholder = st.empty()
    
    with col2.container():
        st.write("##### Usage")
        usage_placeholder = st.empty()

    # Create columns for CPU and memory usage
    col3, col4 = st.columns(2)

    # Placeholders for CPU and memory usage
    with col3.container():
        st.write("##### CPU Usage")
        cpu_placeholder = st.empty()
    
    with col4.container():
        st.write("##### Memory Usage")
        memory_placeholder = st.empty()

    # Initialize latency data
    latency_data = []
    cpu_data = []

    while True:
        # Update latency data
        latency = os.popen("ping -n 1 google.com").read()
        try:
            latency_ms = float(latency.split('time=')[1].split('ms')[0])
        except (IndexError, ValueError):
            latency_ms = None  # Handle the case where the ping command fails or returns unexpected output

        if latency_ms is not None:
            latency_data.append({'Time': time.strftime("%H:%M:%S"), 'Latency (ms)': latency_ms})
            if len(latency_data) > 10:  # Keep only the last 10 data points
                latency_data.pop(0)

            df_latency = pd.DataFrame(latency_data)
            fig, ax = plt.subplots(figsize=(10, 2.5))
            df_latency.set_index('Time').plot(ax=ax)
            plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
            
            # Add interactive tooltips
            cursor = mplcursors.cursor(ax, hover=True)
            cursor.connect("add", lambda sel: sel.annotation.set_text(f"{df_latency.iloc[sel.target.index]}"))

            latency_placeholder.pyplot(fig)

        # Update bandwidth data
        net_io = psutil.net_io_counters()
        data = {
            'Metric': ['Bytes Sent', 'Bytes Received'],
            'Value': [net_io.bytes_sent, net_io.bytes_recv]
        }
        df_bandwidth = pd.DataFrame(data)
        
        fig, ax = plt.subplots()
        bars = ax.bar(df_bandwidth['Metric'], df_bandwidth['Value'])
        ax.set_ylabel('Bytes')
        ax.set_title('Bandwidth Usage')
        
        # Add numerical values inside the bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval}', va='bottom')  # va: vertical alignment

        bandwidth_placeholder.pyplot(fig)

        # Update usage data
        labels = ['Bytes Sent', 'Bytes Received']
        sizes = [net_io.bytes_sent, net_io.bytes_recv]
        fig, ax = plt.subplots(figsize=(4, 4))  # Reduce the size of the pie chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        usage_placeholder.pyplot(fig)

        # Update CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_data.append({'Time': time.strftime("%H:%M:%S"), 'CPU Usage (%)': cpu_usage})
        if len(cpu_data) > 10:  # Keep only the last 10 data points
            cpu_data.pop(0)

        df_cpu = pd.DataFrame(cpu_data)
        fig, ax = plt.subplots()
        df_cpu.set_index('Time').plot(ax=ax)
        ax.axhline(y=80, color='r', linestyle='--')
        plt.xticks(rotation=45)  # Rotate x-axis labels
        cpu_placeholder.pyplot(fig)

        # Update memory usage
        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        fig, ax = plt.subplots()
        bars = ax.bar(['Memory Usage'], [memory_usage], color='green' if memory_usage < 75 else 'red')
        ax.set_ylim(0, 100)
        ax.bar_label(bars, fmt='%.2f%%')
        memory_placeholder.pyplot(fig)

        time.sleep(5)  # Wait for 1 second before updating again

if __name__ == "__main__":
    main()
