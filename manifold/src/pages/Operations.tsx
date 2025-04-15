import React from 'react';
import { Typography, Card, Tabs, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

const Operations: React.FC = () => {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <Title level={2}>Operations Core</Title>
          <Paragraph>Manage your core business operations and ERP functions.</Paragraph>
        </div>
        <Button type="primary" icon={<PlusOutlined />}>
          New Transaction
        </Button>
      </div>
      
      <Card>
        <Tabs defaultActiveKey="sales">
          <TabPane tab="Sales" key="sales">
            <p>Sales module content will be displayed here.</p>
          </TabPane>
          <TabPane tab="Purchases" key="purchases">
            <p>Purchases module content will be displayed here.</p>
          </TabPane>
          <TabPane tab="Inventory" key="inventory">
            <p>Inventory module content will be displayed here.</p>
          </TabPane>
          <TabPane tab="Accounting" key="accounting">
            <p>Accounting module content will be displayed here.</p>
          </TabPane>
          <TabPane tab="HR" key="hr">
            <p>Human Resources module content will be displayed here.</p>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Operations;