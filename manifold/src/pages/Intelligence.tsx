import React from 'react';
import { Typography, Card, Tabs, Button, Row, Col } from 'antd';
import { LineChartOutlined, BarChartOutlined, PieChartOutlined, DotChartOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

const Intelligence: React.FC = () => {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Synapse™ Intelligence</Title>
          <Paragraph>Business intelligence, analytics, and predictive insights.</Paragraph>
        </div>
        <Button type="primary" icon={<LineChartOutlined />}>
          Create Report
        </Button>
      </div>
      
      <Card>
        <Tabs defaultActiveKey="dashboards">
          <TabPane tab="Dashboards" key="dashboards">
            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Card
                  hoverable
                  cover={<div style={{ height: 120, background: '#f0f2f5', display: 'flex', justifyContent: 'center', alignItems: 'center' }}><LineChartOutlined style={{ fontSize: 48, color: '#1890ff' }} /></div>}
                >
                  <Card.Meta title="Sales Performance" description="Real-time sales metrics and KPIs" />
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  hoverable
                  cover={<div style={{ height: 120, background: '#f0f2f5', display: 'flex', justifyContent: 'center', alignItems: 'center' }}><BarChartOutlined style={{ fontSize: 48, color: '#52c41a' }} /></div>}
                >
                  <Card.Meta title="Financial Overview" description="P&L, cash flow, and financial health" />
                </Card>
              </Col>
              <Col span={8}>
                <Card
                  hoverable
                  cover={<div style={{ height: 120, background: '#f0f2f5', display: 'flex', justifyContent: 'center', alignItems: 'center' }}><PieChartOutlined style={{ fontSize: 48, color: '#722ed1' }} /></div>}
                >
                  <Card.Meta title="Inventory Analysis" description="Stock levels, turnover, and forecasts" />
                </Card>
              </Col>
            </Row>
          </TabPane>
          <TabPane tab="Forecasts" key="forecasts">
            <p>Predictive forecasts and trend analysis will be displayed here.</p>
          </TabPane>
          <TabPane tab="Reports" key="reports">
            <p>Standard and custom reports will be displayed here.</p>
          </TabPane>
          <TabPane tab="What-If Analysis" key="whatif">
            <p>Scenario planning and simulation tools will be displayed here.</p>
          </TabPane>
          <TabPane tab="Strategic Advisor" key="advisor">
            <p>AI-driven strategic recommendations will be displayed here.</p>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Intelligence;