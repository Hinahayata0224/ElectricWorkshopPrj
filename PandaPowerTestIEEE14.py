import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


# 设置中文字体支持
def set_chinese_font():
    """
    设置中文字体支持，解决中文显示问题
    """
    try:
        # 尝试使用系统中已有的中文字体
        font_list = [f.name for f in font_manager.fontManager.ttflist]
        chinese_fonts = ['SimHei', 'Microsoft YaHei', 'STHeiti', 'STKaiti', 'STSong', 'STFangsong']

        for font in chinese_fonts:
            if font in font_list:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                print(f"使用字体: {font}")
                return True

        # 如果没有找到中文字体，使用默认字体并提示
        print("警告: 未找到中文字体，中文显示可能不正常")
        return False
    except:
        print("警告: 字体设置失败，使用默认字体")
        return False


def create_ieee14_network():
    """
    创建IEEE 14节点测试系统
    """
    net = nw.case14()
    return net


def run_power_flow(net):
    """
    执行潮流计算
    """
    pp.runpp(net)
    return net


def plot_network_topology(net):
    """
    绘制网络拓扑图
    """
    # 创建图形
    plt.figure(figsize=(12, 8))

    # 绘制总线
    bus_colors = ['b' if bt == 'b' else 'g' for bt in net.bus.type.values]
    bus_plot = plot.create_bus_collection(net, size=0.1, color=bus_colors, zorder=10)

    # 绘制线路
    line_colors = ['r' if l.in_service else 'gray' for l in net.line.itertuples()]
    line_plot = plot.create_line_collection(net, color=line_colors, linewidth=1.0, use_bus_geodata=True)

    # 绘制变压器
    trafo_plot = plot.create_trafo_collection(net, color='purple', linewidth=1.5)

    # 绘制负载
    load_plot = plot.create_load_collection(net, size=0.08, color='orange', zorder=11)

    # 绘制发电机
    gen_plot = plot.create_gen_collection(net, size=0.08, color='yellow', zorder=11)

    # 添加到图形
    plot.draw_collections([line_plot, trafo_plot, bus_plot, load_plot, gen_plot], figsize=(12, 8))

    plt.title("IEEE 14节点系统拓扑图")
    plt.tight_layout()
    plt.savefig("ieee14_topology.png", dpi=300)
    plt.show()


def output_node_voltages(net):
    """
    输出各节点电压
    """
    print("=" * 50)
    print("各节点电压结果:")
    print("=" * 50)

    # 创建节点电压数据框
    voltage_df = pd.DataFrame({
        '节点': net.bus.name.values,
        '电压幅值(pu)': np.round(net.res_bus.vm_pu.values, 4),
        '电压角度(度)': np.round(net.res_bus.va_degree.values, 2),
    })

    print(voltage_df.to_string(index=False))
    return voltage_df


def output_node_power(net):
    """
    输出各节点功率
    """
    print("\n" + "=" * 50)
    print("各节点功率结果:")
    print("=" * 50)

    # 创建节点功率数据框
    power_df = pd.DataFrame({
        '节点': net.bus.name.values,
        '有功功率(MW)': np.round(net.res_bus.p_mw.values, 2),
        '无功功率(MVar)': np.round(net.res_bus.q_mvar.values, 2)
    })

    print(power_df.to_string(index=False))
    return power_df


def output_line_loading(net):
    """
    输出各线路负载
    """
    print("\n" + "=" * 50)
    print("各线路负载结果:")
    print("=" * 50)

    # 创建线路负载数据框
    loading_df = pd.DataFrame({
        '从节点': net.line.from_bus.values,
        '到节点': net.line.to_bus.values,
        '负载率(%)': np.round(net.res_line.loading_percent.values, 2),
        '有功功率(MW)': np.round(net.res_line.p_from_mw.values, 2),
        '无功功率(MVar)': np.round(net.res_line.q_from_mvar.values, 2)
    })

    # 添加节点名称
    bus_names = net.bus.name.values
    loading_df['从节点名称'] = [bus_names[i] for i in loading_df['从节点']]
    loading_df['到节点名称'] = [bus_names[i] for i in loading_df['到节点']]

    # 重新排列列
    loading_df = loading_df[['从节点', '从节点名称', '到节点', '到节点名称',
                             '负载率(%)', '有功功率(MW)', '无功功率(MVar)']]

    print(loading_df.to_string(index=False))
    return loading_df


def output_power_losses(net):
    """
    输出功率损耗
    """
    print("\n" + "=" * 50)
    print("功率损耗结果:")
    print("=" * 50)

    # 线路损耗
    line_losses = pd.DataFrame({
        '从节点': net.line.from_bus.values,
        '到节点': net.line.to_bus.values,
        '有功损耗(MW)': np.round(net.res_line.pl_mw.values, 4),
        '无功损耗(MVar)': np.round(net.res_line.ql_mvar.values, 4)
    })

    # 添加节点名称
    bus_names = net.bus.name.values
    line_losses['从节点名称'] = [bus_names[i] for i in line_losses['从节点']]
    line_losses['到节点名称'] = [bus_names[i] for i in line_losses['到节点']]

    # 重新排列列
    line_losses = line_losses[['从节点', '从节点名称', '到节点', '到节点名称',
                               '有功损耗(MW)', '无功损耗(MVar)']]

    print("线路损耗:")
    print(line_losses.to_string(index=False))

    # 变压器损耗
    trafo_losses = pd.DataFrame({
        '高压侧节点': net.trafo.hv_bus.values,
        '低压侧节点': net.trafo.lv_bus.values,
        '有功损耗(MW)': np.round(net.res_trafo.pl_mw.values, 4),
        '无功损耗(MVar)': np.round(net.res_trafo.ql_mvar.values, 4)
    })

    # 添加节点名称
    trafo_losses['高压侧节点名称'] = [bus_names[i] for i in trafo_losses['高压侧节点']]
    trafo_losses['低压侧节点名称'] = [bus_names[i] for i in trafo_losses['低压侧节点']]

    # 重新排列列
    trafo_losses = trafo_losses[['高压侧节点', '高压侧节点名称', '低压侧节点', '低压侧节点名称',
                                 '有功损耗(MW)', '无功损耗(MVar)']]

    print("\n变压器损耗:")
    print(trafo_losses.to_string(index=False))

    # 总损耗
    total_p_loss = np.sum(net.res_line.pl_mw.values) + np.sum(net.res_trafo.pl_mw.values)
    total_q_loss = np.sum(net.res_line.ql_mvar.values) + np.sum(net.res_trafo.ql_mvar.values)

    print("\n总损耗:")
    print(f"总有功损耗: {total_p_loss:.4f} MW")
    print(f"总无功损耗: {total_q_loss:.4f} MVar")

    return line_losses, trafo_losses, total_p_loss, total_q_loss


def main():
    """
    主函数
    """

    # 设置中文字体
    set_chinese_font()
    
    # 创建IEEE 14节点系统
    print("创建IEEE 14节点系统...")
    net = create_ieee14_network()

    # 执行潮流计算
    print("执行潮流计算...")
    net = run_power_flow(net)

    # 绘制网络拓扑图
    print("绘制网络拓扑图...")
    # plot_network_topology(net)

    # 输出节点电压
    voltage_df = output_node_voltages(net)

    # 输出节点功率
    power_df = output_node_power(net)

    # 输出线路负载
    loading_df = output_line_loading(net)

    # 输出功率损耗
    line_losses, trafo_losses, total_p_loss, total_q_loss = output_power_losses(net)

    # 保存结果到CSV文件
    voltage_df.to_csv("node_voltages.csv", index=False)
    power_df.to_csv("node_power.csv", index=False)
    loading_df.to_csv("line_loading.csv", index=False)
    line_losses.to_csv("line_losses.csv", index=False)
    trafo_losses.to_csv("trafo_losses.csv", index=False)

    with open("total_losses.txt", "w") as f:
        f.write(f"总有功损耗: {total_p_loss:.4f} MW\n")
        f.write(f"总无功损耗: {total_q_loss:.4f} MVar\n")

    print("\n所有结果已保存到文件!")


if __name__ == "__main__":
    main()
