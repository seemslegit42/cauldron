import React, { useState, useEffect } from 'react';
import { Layout, Typography, Input, Avatar, Card, List, Tag, Tooltip, Button, Divider, Drawer, Tabs } from 'antd';
import { 
  SearchOutlined, 
  BulbOutlined, 
  RobotOutlined, 
  UserOutlined, 
  MessageOutlined,
  BellOutlined,
  InfoCircleOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import ProCard from '@ant-design/pro-card';
import { ProList } from '@ant-design/pro-components';

const { Header, Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { TabPane } = Tabs;

/**
 * SymbioticInterface Component
 * 
 * A fluid, conversational control interface that proactively surfaces information
 * and provides context-aware interactions with the Cauldron system.
 */
const SymbioticInterface: React.FC = () => {
  const [commandPaletteVisible, setCommandPaletteVisible] = useState(false);
  const [agentInsightsVisible, setAgentInsightsVisible] = useState(false);
  const [contextualDrawerVisible, setContextualDrawerVisible] = useState(false);
  const [currentContext, setCurrentContext] = useState<any>(null);
  
  // Simulated proactive insights that would come from agents
  const [proactiveInsights, setProactiveInsights] = useState([
    {
      id: '1',
      title: 'Inventory Alert',
      description: 'Stock levels for SKU-1234 are below threshold. Consider reordering.',
      source: 'Inventory Agent',
      priority: 'high',
      timestamp: new Date().toISOString(),
      actions: ['View Details', 'Create PO'],
      confidence: 0.92,
    },
    {
      id: '2',
      title: 'Customer Opportunity',
      description: 'ABC Corp has increased order frequency by 35% this quarter. Potential upsell opportunity.',
      source: 'Sales Insights Agent',
      priority: 'medium',
      timestamp: new Date().toISOString(),
      actions: ['View Analysis', 'Contact Customer'],
      confidence: 0.87,
    },
    {
      id: '3',
      title: 'Process Optimization',
      description: 'Detected inefficiency in approval workflow. 3 steps could be automated.',
      source: 'Process Optimization Agent',
      priority: 'low',
      timestamp: new Date().toISOString(),
      actions: ['View Suggestion', 'Implement Change'],
      confidence: 0.78,
    },
  ]);

  // Simulated conversation history
  const [conversationHistory, setConversationHistory] = useState([
    {
      id: '1',
      sender: 'user',
      message: 'Show me sales performance for Q2',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: '2',
      sender: 'system',
      message: 'Here\'s the Q2 sales performance dashboard. Overall sales are up 12% compared to Q1, with the strongest growth in the Enterprise segment.',
      timestamp: new Date(Date.now() - 3590000).toISOString(),
      attachments: ['Sales Dashboard'],
    },
    {
      id: '3',
      sender: 'user',
      message: 'Which products had the highest growth?',
      timestamp: new Date(Date.now() - 3580000).toISOString(),
    },
    {
      id: '4',
      sender: 'system',
      message: 'Product X had the highest growth at 28%, followed by Product Y at 22%. Would you like to see the detailed product breakdown?',
      timestamp: new Date(Date.now() - 3570000).toISOString(),
    },
  ]);

  // Simulated contextual information
  const [contextualInfo, setContextualInfo] = useState([
    {
      id: '1',
      title: 'Recent Sales Order',
      description: 'SO-2023-0456 was created 15 minutes ago for Customer XYZ',
      type: 'document',
      link: '/sales-order/SO-2023-0456',
    },
    {
      id: '2',
      title: 'Upcoming Meeting',
      description: 'Strategy Review with Marketing Team at 2:00 PM',
      type: 'calendar',
      link: '/calendar/meeting-123',
    },
    {
      id: '3',
      title: 'Related Knowledge',
      description: 'Marketing Strategy Document (2023) might be relevant to your current task',
      type: 'knowledge',
      link: '/lore/document-456',
    },
  ]);

  // Handle command palette input
  const handleCommandSearch = (value: string) => {
    console.log('Command entered:', value);
    // In a real implementation, this would process the command
    // and update the conversation history
    
    const newMessage = {
      id: Date.now().toString(),
      sender: 'user',
      message: value,
      timestamp: new Date().toISOString(),
    };
    
    setConversationHistory([...conversationHistory, newMessage]);
    
    // Simulate system response
    setTimeout(() => {
      const systemResponse = {
        id: (Date.now() + 1).toString(),
        sender: 'system',
        message: `I'm processing your request: "${value}". This would be replaced with an actual response from the system.`,
        timestamp: new Date().toISOString(),
      };
      setConversationHistory(prev => [...prev, systemResponse]);
    }, 1000);
  };

  // Show contextual information for a specific item
  const showContextualInfo = (item: any) => {
    setCurrentContext(item);
    setContextualDrawerVisible(true);
  };

  // Keyboard shortcut to open command palette (Ctrl+K or Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteVisible(true);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <Layout style={{ height: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0, marginRight: 24 }}>Cauldron™</Title>
          <Button 
            type="text" 
            icon={<SearchOutlined />} 
            onClick={() => setCommandPaletteVisible(true)}
          >
            Search or type a command... (Ctrl+K)
          </Button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Tooltip title="Agent Insights">
            <Button 
              type="text" 
              icon={<BulbOutlined />} 
              onClick={() => setAgentInsightsVisible(true)}
              badge={{ count: proactiveInsights.length }}
            />
          </Tooltip>
          <Tooltip title="Contextual Information">
            <Button 
              type="text" 
              icon={<InfoCircleOutlined />} 
              onClick={() => setContextualDrawerVisible(true)}
              badge={{ count: contextualInfo.length }}
            />
          </Tooltip>
          <Tooltip title="Notifications">
            <Button type="text" icon={<BellOutlined />} badge={{ count: 5 }} />
          </Tooltip>
          <Avatar icon={<UserOutlined />} style={{ marginLeft: 16 }} />
        </div>
      </Header>
      
      <Layout>
        <Content style={{ padding: '24px', overflow: 'auto' }}>
          {/* Main content would go here - this would be the primary workspace */}
          <ProCard title="Workspace" style={{ marginBottom: 24 }}>
            <Paragraph>
              This is the main workspace area where the primary content would be displayed.
              It could show dashboards, forms, reports, or other content based on the user's current task.
            </Paragraph>
          </ProCard>
          
          {/* Conversation Interface */}
          <ProCard 
            title="Conversation Interface" 
            extra={<Button type="link" icon={<MessageOutlined />}>Expand</Button>}
          >
            <List
              itemLayout="horizontal"
              dataSource={conversationHistory}
              renderItem={item => (
                <List.Item style={{ 
                  textAlign: item.sender === 'user' ? 'right' : 'left',
                  padding: '8px 16px'
                }}>
                  <List.Item.Meta
                    avatar={item.sender === 'user' ? 
                      <Avatar icon={<UserOutlined />} /> : 
                      <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#1890ff' }} />
                    }
                    title={<Text strong>{item.sender === 'user' ? 'You' : 'Cauldron'}</Text>}
                    description={
                      <div>
                        <Paragraph>{item.message}</Paragraph>
                        {item.attachments && item.attachments.map((attachment, index) => (
                          <Tag key={index} color="blue">{attachment}</Tag>
                        ))}
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
            <Divider style={{ margin: '12px 0' }} />
            <Search
              placeholder="Ask a question or enter a command..."
              enterButton="Send"
              size="large"
              onSearch={handleCommandSearch}
            />
          </ProCard>
        </Content>
      </Layout>
      
      {/* Command Palette Drawer */}
      <Drawer
        title="Runestone Command Palette"
        placement="top"
        height={400}
        visible={commandPaletteVisible}
        onClose={() => setCommandPaletteVisible(false)}
        destroyOnClose
      >
        <Search
          placeholder="Search or type a command..."
          size="large"
          autoFocus
          onSearch={handleCommandSearch}
        />
        <Tabs defaultActiveKey="1" style={{ marginTop: 16 }}>
          <TabPane tab="Recent" key="1">
            <List
              itemLayout="horizontal"
              dataSource={conversationHistory.slice(-3).reverse()}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={item.sender === 'user' ? 
                      <Avatar icon={<UserOutlined />} /> : 
                      <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#1890ff' }} />
                    }
                    title={item.message}
                    description={new Date(item.timestamp).toLocaleTimeString()}
                  />
                  <Button type="link" icon={<ArrowRightOutlined />} />
                </List.Item>
              )}
            />
          </TabPane>
          <TabPane tab="Suggested" key="2">
            <List
              itemLayout="horizontal"
              dataSource={[
                'Show sales dashboard for current month',
                'Create new purchase order',
                'Find documents related to Project X',
                'Schedule meeting with marketing team'
              ]}
              renderItem={item => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<BulbOutlined />} style={{ backgroundColor: '#52c41a' }} />}
                    title={item}
                  />
                  <Button type="link" icon={<ArrowRightOutlined />} />
                </List.Item>
              )}
            />
          </TabPane>
        </Tabs>
      </Drawer>
      
      {/* Agent Insights Drawer */}
      <Drawer
        title="Agent Insights"
        placement="right"
        width={500}
        visible={agentInsightsVisible}
        onClose={() => setAgentInsightsVisible(false)}
      >
        <ProList
          itemLayout="vertical"
          rowKey="id"
          dataSource={proactiveInsights}
          metas={{
            title: {
              dataIndex: 'title',
              render: (text, record) => (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Text strong>{text}</Text>
                  <Tag color={
                    record.priority === 'high' ? 'red' : 
                    record.priority === 'medium' ? 'orange' : 'green'
                  }>
                    {record.priority.toUpperCase()}
                  </Tag>
                </div>
              ),
            },
            description: {
              dataIndex: 'description',
            },
            content: {
              render: (_, record) => (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Text type="secondary">Source: {record.source}</Text>
                    <Tooltip title="Confidence Score">
                      <Tag color="blue">{Math.round(record.confidence * 100)}% confidence</Tag>
                    </Tooltip>
                  </div>
                  <div>
                    {record.actions.map((action, index) => (
                      <Button key={index} type={index === 0 ? "primary" : "default"} size="small" style={{ marginRight: 8 }}>
                        {action}
                      </Button>
                    ))}
                  </div>
                </div>
              ),
            },
          }}
        />
      </Drawer>
      
      {/* Contextual Information Drawer */}
      <Drawer
        title="Contextual Information"
        placement="right"
        width={500}
        visible={contextualDrawerVisible}
        onClose={() => setContextualDrawerVisible(false)}
      >
        {currentContext ? (
          <div>
            <Title level={4}>{currentContext.title}</Title>
            <Paragraph>{currentContext.description}</Paragraph>
            <Button type="primary" href={currentContext.link}>View Details</Button>
            <Divider />
            <Button onClick={() => setCurrentContext(null)}>Back to List</Button>
          </div>
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={contextualInfo}
            renderItem={item => (
              <List.Item 
                actions={[
                  <Button type="link" onClick={() => showContextualInfo(item)}>Details</Button>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar icon={
                      item.type === 'document' ? <SearchOutlined /> :
                      item.type === 'calendar' ? <BellOutlined /> :
                      <BulbOutlined />
                    } />
                  }
                  title={item.title}
                  description={item.description}
                />
              </List.Item>
            )}
          />
        )}
      </Drawer>
    </Layout>
  );
};

export default SymbioticInterface;