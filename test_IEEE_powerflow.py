"""
IEEE标准14节点系统潮流计算验证程序
"""

import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandapower as pp
import pandapower.networks as nw

warnings.filterwarnings('ignore')


def create_network_topology(net, title="ieee14 system"):
    """创建并显示网络拓扑图"""
    try:
        print(f"\n正在绘制拓扑图: {title}")

        # 创建图形
        fig, ax = plt.subplots(figsize=(12, 10))

        # 使用改进的布局算法
        n_buses = len(net.bus)

        # 创建连接矩阵
        adjacency = np.zeros((n_buses, n_buses))

        # 标记线路连接
        for _, line in net.line.iterrows():
            from_bus = line.from_bus
            to_bus = line.to_bus
            if from_bus < n_buses and to_bus < n_buses:
                adjacency[from_bus, to_bus] = 1
                adjacency[to_bus, from_bus] = 1

        # 标记变压器连接
        for _, trafo in net.trafo.iterrows():
            hv_bus = trafo.hv_bus
            lv_bus = trafo.lv_bus
            if hv_bus < n_buses and lv_bus < n_buses:
                adjacency[hv_bus, lv_bus] = 2  # 用2表示变压器连接
                adjacency[lv_bus, hv_bus] = 2

        # 生成节点位置（环形布局）
        center_x, center_y = 0, 0
        radius = 8
        positions = {}

        for i in range(n_buses):
            angle = 2 * np.pi * i / n_buses
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            positions[i] = (x, y)

        # 绘制连接线
        for i in range(n_buses):
            for j in range(i + 1, n_buses):
                if adjacency[i, j] == 1:  # 线路
                    if i in positions and j in positions:
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        ax.plot([x1, x2], [y1, y2], 'gray', linewidth=1.5, alpha=0.7)
                elif adjacency[i, j] == 2:  # 变压器
                    if i in positions and j in positions:
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        ax.plot([x1, x2], [y1, y2], 'blue', linewidth=2.5, alpha=0.8, linestyle='--')

        # 绘制节点
        x_coords = [pos[0] for pos in positions.values()]
        y_coords = [pos[1] for pos in positions.values()]

        # 标记不同类型的节点
        gen_buses = set(net.gen.bus.values) if len(net.gen) > 0 else set()
        load_buses = set(net.load.bus.values) if len(net.load) > 0 else set()
        ext_grid_buses = set(net.ext_grid.bus.values) if len(net.ext_grid) > 0 else set()

        for bus_id, (x, y) in positions.items():
            if bus_id in ext_grid_buses:
                color = 'red'
                marker = 's'
                size = 120
                label = '外部电网'
            elif bus_id in gen_buses:
                color = 'green'
                marker = '^'
                size = 100
                label = '发电机'
            elif bus_id in load_buses:
                color = 'orange'
                marker = 'v'
                size = 100
                label = '负载'
            else:
                color = 'lightblue'
                marker = 'o'
                size = 80
                label = '总线'

            ax.scatter(x, y, s=size, c=color, marker=marker, edgecolors='black', alpha=0.8)
            ax.text(x, y, f'{bus_id}', ha='center', va='center',
                    fontweight='bold', fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.3'))

        # 添加图例
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='ext_grid'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='green', markersize=10, label='gen'),
            Line2D([0], [0], marker='v', color='w', markerfacecolor='orange', markersize=10, label='load'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='bus'),
            Line2D([0], [0], color='gray', linewidth=2, label='line'),
            Line2D([0], [0], color='blue', linewidth=2, linestyle='--', label='trans')
        ]

        ax.legend(handles=legend_elements, loc='upper right')

        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel('axis X')
        ax.set_ylabel('axis Y')
        ax.grid(True, alpha=0.3)

        # 设置坐标轴范围
        margin = 2
        ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
        ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)

        plt.tight_layout()

        # 显示图形
        print("✓ 拓扑图绘制完成，正在显示...")
        plt.show()

        # 保存图片
        plt.savefig('ieee14拓扑.png', dpi=300, bbox_inches='tight')
        print("✓ 拓扑图已保存为 'ieee14拓扑.png'")

        return True

    except Exception as e:
        print(f"⚠ 拓扑图绘制失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_detailed_results():
    """显示详细计算结果"""
    print("\n" + "=" * 60)
    print("IEEE 14节点系统详细计算结果")
    print("=" * 60)

    try:
        net = nw.case14()
        pp.runpp(net)

        # 显示总线信息
        print("\n总线信息:")
        for i, bus in net.bus.iterrows():
            voltage = net.res_bus.vm_pu.loc[i]
            angle = net.res_bus.va_degree.loc[i]
            print(f"  Bus {i} ({bus['name']}): {voltage:.3f} p.u., {angle:.1f}°")

        # 显示发电机信息
        print("\n发电机信息:")
        for i, gen in net.gen.iterrows():
            p_mw = net.res_gen.p_mw.loc[i]
            q_mvar = net.res_gen.q_mvar.loc[i]
            print(f"  Gen {i} at Bus {gen.bus}: {p_mw:.2f} MW, {q_mvar:.2f} MVar")

        # 显示负载信息
        print("\n负载信息:")
        for i, load in net.load.iterrows():
            print(f"  Load {i} at Bus {load.bus}: {load.p_mw:.2f} MW, {load.q_mvar:.2f} MVar")

        # 显示外部电网
        print("\n外部电网:")
        for i, ext_grid in net.ext_grid.iterrows():
            p_mw = net.res_ext_grid.p_mw.loc[i]
            print(f"  Ext Grid at Bus {ext_grid.bus}: {p_mw:.2f} MW")

    except Exception as e:
        print(f"显示详细结果失败: {e}")


'''
def plot_voltage_profile(net, title="总线电压分布图"):
    """绘制电压分布图"""
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 绘制电压分布
        bus_ids = net.bus.index
        voltages = net.res_bus.vm_pu.values
        
        bars = ax1.bar(bus_ids, voltages, color='skyblue', edgecolor='navy', alpha=0.8)
        # 标记电压异常的总线
        for i, voltage in enumerate(voltages):
            if voltage < 0.95 or voltage > 1.05:
                bars[i].set_color('red')
        
        ax1.set_xlabel('总线编号')
        ax1.set_ylabel('电压 (p.u.)')
        ax1.set_title('各总线电压值')
        ax1.axhline(y=1.0, color='r', linestyle='--', alpha=0.7, label='额定电压')
        ax1.axhline(y=0.95, color='orange', linestyle='--', alpha=0.7, label='电压下限')
        ax1.axhline(y=1.05, color='purple', linestyle='--', alpha=0.7, label='电压上限')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 绘制电压相角
        angles = net.res_bus.va_degree.values
        
        ax2.bar(bus_ids, angles, color='lightgreen', edgecolor='darkgreen', alpha=0.8)
        ax2.set_xlabel('总线编号')
        ax2.set_ylabel('相角 (度)')
        ax2.set_title('各总线电压相角')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 显示图形
        print("✓ 电压分布图绘制完成，正在显示...")
        plt.show()
        
        plt.savefig('voltage_profile.png', dpi=300, bbox_inches='tight')
        print("✓ 电压分布图已保存为 'voltage_profile.png'")
        
    except Exception as e:
        print(f"⚠ 电压分布图绘制失败: {e}")
'''


def test_ieee_powerflow():
    """测试IEEE标准系统潮流计算"""
    print("=" * 60)
    print("IEEE标准节点系统潮流计算验证")
    print(f"pandapower版本: {pp.__version__}")
    print("=" * 60)

    success = True

    try:
        # 测试1: 导入IEEE 14节点系统
        print("\n1. 导入IEEE 14节点系统...")
        net14 = nw.case14()
        print("✓ IEEE 14节点系统导入成功")
        print(f"   总线数量: {len(net14.bus)}")
        print(f"   线路数量: {len(net14.line)}")
        print(f"   变压器数量: {len(net14.trafo)}")
        print(f"   发电机数量: {len(net14.gen)}")
        print(f"   负载数量: {len(net14.load)}")
        print(f"   外部电网数量: {len(net14.ext_grid)}")

        # 在线绘制拓扑图
        create_network_topology(net14, "IEEE 14节点系统拓扑图")

        # 测试2: 运行潮流计算
        print("\n2. 运行潮流计算...")
        pp.runpp(net14)
        print("✓ 潮流计算完成")
        print(f"   收敛状态: {net14.converged}")

        # 测试3: 显示计算结果
        print("\n3. 计算结果摘要:")
        print(f"   系统总有功负载: {net14.load.p_mw.sum():.3f} MW")
        print(f"   系统总无功负载: {net14.load.q_mvar.sum():.3f} MVar")
        print(f"   外部电网注入: {net14.res_ext_grid.p_mw.sum():.3f} MW")
        print(f"   发电机出力: {net14.res_gen.p_mw.sum():.3f} MW")

        # 计算网损和平衡
        line_losses = net14.res_line.pl_mw.sum()
        trafo_losses = net14.res_trafo.pl_mw.sum() if len(net14.trafo) > 0 else 0
        total_losses = line_losses + trafo_losses

        total_gen = net14.res_ext_grid.p_mw.sum() + net14.res_gen.p_mw.sum()
        total_load = net14.load.p_mw.sum()
        balance = total_gen - total_load - total_losses

        print(f"   线路损耗: {line_losses:.3f} MW")
        print(f"   变压器损耗: {trafo_losses:.3f} MW")
        print(f"   总网损: {total_losses:.3f} MW")
        print(f"   功率平衡差: {balance:.6f} MW")

        if abs(balance) < 0.001:
            print("   ✓ 功率平衡良好")
        else:
            print(f"   ⚠ 功率平衡误差: {abs(balance / total_gen * 100):.6f}%")

        # 显示总线电压
        print("\n4. 总线电压情况 (p.u.):")
        max_voltage = net14.res_bus.vm_pu.max()
        min_voltage = net14.res_bus.vm_pu.min()
        print(f"   最高电压: {max_voltage:.3f} at bus {net14.res_bus.vm_pu.idxmax()}")
        print(f"   最低电压: {min_voltage:.3f} at bus {net14.res_bus.vm_pu.idxmin()}")
        print(f"   平均电压: {net14.res_bus.vm_pu.mean():.3f}")

        if min_voltage > 0.9 and max_voltage < 1.1:
            print("   ✓ 电压水平正常")
        else:
            print("   ⚠ 电压水平异常")

    except Exception as e:
        print(f"❌ 主要测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return success


'''
        # 绘制电压分布图
        plot_voltage_profile(net14, "IEEE 14节点系统电压分布")

        # 测试4: 测试其他IEEE标准系统
        print("\n5. 测试其他IEEE标准系统...")
        test_cases = [
            ("IEEE 9节点", nw.case9),
            ("IEEE 30节点", nw.case30),
            ("IEEE 57节点", nw.case57)
        ]
        
        for case_name, case_func in test_cases:
            try:
                net = case_func()
                pp.runpp(net)
                status = "收敛" if net.converged else "发散"
                print(f"   ✓ {case_name}: {len(net.bus)}总线, {status}")
                
                # 可选：绘制其他系统的拓扑图
                if user_input := input(f"   是否绘制{case_name}拓扑图？(y/n): ").lower() == 'y':
                    create_network_topology(net, f"{case_name}拓扑图")
                    
            except Exception as e:
                print(f"   ⚠ {case_name}: 不可用 - {str(e)[:50]}...")

        # 测试5: 创建简单的自定义测试网络
        print("\n6. 创建自定义测试网络...")
        try:
            net_test = pp.create_empty_network()
            
            # 创建总线
            b1 = pp.create_bus(net_test, vn_kv=110, name="高压母线")
            b2 = pp.create_bus(net_test, vn_kv=20, name="中压母线")
            b3 = pp.create_bus(net_test, vn_kv=20, name="负载母线")
            
            # 创建外部电网
            pp.create_ext_grid(net_test, bus=b1, vm_pu=1.02, name="主网")
            
            # 创建变压器
            pp.create_transformer(net_test, hv_bus=b1, lv_bus=b2, 
                                 std_type="25 MVA 110/20 kV", name="主变压器")
            
            # 创建负载
            pp.create_load(net_test, bus=b3, p_mw=2.5, q_mvar=1.2, name="工业负载")
            
            # 创建线路
            pp.create_line(net_test, from_bus=b2, to_bus=b3, length_km=5,
                          std_type="NA2XS2Y 1x185 RM/25 12/20 kV", name="馈线")
            
            # 运行计算
            pp.runpp(net_test)
            
            print("   ✓ 自定义网络测试成功")
            print(f"     负载电压: {net_test.res_bus.vm_pu.loc[b3]:.3f} p.u.")
            
            line_loading = net_test.res_line.loading_percent.values[0]
            print(f"     线路负载率: {line_loading:.1f}%")
            
            if line_loading > 100:
                print(f"   ⚠ 警告: 线路过载 ({line_loading:.1f}%)")
            else:
                print("   ✓ 线路负载率正常")
                
            # 绘制自定义网络拓扑
            if user_input := input("   是否绘制自定义网络拓扑图？(y/n): ").lower() == 'y':
                create_network_topology(net_test, "自定义测试网络拓扑图")
                
        except Exception as e:
            print(f"   ⚠ 自定义网络测试失败: {str(e)[:50]}...")
            success = False

    except Exception as e:
        print(f"❌ 主要测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return success
'''
if __name__ == "__main__":
    try:
        print("开始pandapower功能验证...")
        print("注意: 程序将显示交互式图表窗口")
        print("请关闭图表窗口以继续程序执行")

        # 设置matplotlib为交互模式
        plt.ion()

        # 运行主要测试
        success = test_ieee_powerflow()

        if success:
            # 显示详细结果
            user_input = input("\n是否显示详细计算结果？(y/n): ")
            if user_input.lower() in ['y', 'yes']:
                display_detailed_results()
            else:
                print("\n" + "=" * 60)
                print("✅ pandapower验证成功！")
                print("✅ 所有基本功能测试通过")
                print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ pandapower验证部分失败")
            print("=" * 60)

        print("\n验证完成！")
        print("所有图表已保存为PNG文件")

        # 保持程序运行，让用户查看最后的图表
        input("按回车键退出程序...")

    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback

        traceback.print_exc()
