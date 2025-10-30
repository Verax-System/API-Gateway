import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Button, Modal, message, Space, Input, Typography, Popconfirm, Tooltip, Card, Avatar, Empty, Spin, Form } from 'antd';
import { motion, AnimatePresence } from 'framer-motion';
import { PlusOutlined, EditOutlined, DeleteOutlined, TeamOutlined, MailOutlined, PhoneOutlined, IdcardOutlined } from '@ant-design/icons';
import ApiService from '../api/ApiService';

const { Title, Text } = Typography;
const { Search } = Input;

// Estilos embutidos (sem alterações)
const PageStyles = () => (
    <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    .supplier-page-container { padding: 24px; background-color: #f0f2f5; font-family: 'Inter', sans-serif; min-height: 100vh; }
    .supplier-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding: 20px 24px; background: linear-gradient(135deg, #16A085 0%, #2980B9 100%); border-radius: 16px; color: white; box-shadow: 0 10px 30px -10px rgba(22, 160, 133, 0.5); }
    .controls-card { margin-bottom: 24px; border-radius: 12px; }
    .supplier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
    .supplier-card { border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #e8e8e8; transition: all 0.3s ease-in-out; position: relative; }
    .supplier-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.12); }
    .card-actions { position: absolute; top: 16px; right: 16px; }
    .contact-info { margin-top: 16px; display: flex; flex-direction: column; gap: 8px; }
  `}</style>
);


// Componente "Filho": O formulário dentro do Modal
const SupplierFormModal = ({ visible, onCancel, onSuccess, editingSupplier }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const isEditing = !!editingSupplier;

    // Popula o formulário se estiver no modo de edição
    useEffect(() => {
        if (isEditing) {
            form.setFieldsValue(editingSupplier);
        } else {
            form.resetFields();
        }
    }, [editingSupplier, isEditing, form]);

    const handleFinish = async (values) => {
        setLoading(true);
        try {
            if (isEditing) {
                // PASSO 1 (CORRIGIDO): Usando o método padrão '.put'
                await ApiService.put(`/suppliers/${editingSupplier.id}`, values);
            } else {
                // PASSO 1 (CORRIGIDO): Usando o método padrão '.post'
                await ApiService.post('/suppliers/', values);
            }

            if (onSuccess) {
                onSuccess(); // Notifica o "pai" sobre o sucesso
            }
        } catch (error) {
            const errorMsg = error.response?.data?.detail || 'Erro ao salvar o fornecedor.';
            message.error(errorMsg);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <Modal
            title={isEditing ? 'Editar Fornecedor' : 'Adicionar Novo Fornecedor'}
            open={visible}
            onCancel={onCancel}
            footer={null}
            destroyOnClose
        >
            <Form form={form} layout="vertical" onFinish={handleFinish}>
                <Form.Item name="name" label="Nome do Fornecedor" rules={[{ required: true, message: 'Por favor, insira o nome!' }]}>
                    <Input prefix={<TeamOutlined />} placeholder="Ex: Distribuidora de Bebidas LTDA" size="large" />
                </Form.Item>
                <Form.Item name="contact_person" label="Pessoa de Contato">
                    <Input prefix={<IdcardOutlined />} placeholder="Ex: Carlos Silva" size="large" />
                </Form.Item>
                <Form.Item name="email" label="E-mail" rules={[{ type: 'email', message: 'Por favor, insira um e-mail válido!' }]}>
                    <Input prefix={<MailOutlined />} placeholder="Ex: contato@distribuidora.com" size="large" />
                </Form.Item>
                <Form.Item name="phone_number" label="Telefone">
                    <Input prefix={<PhoneOutlined />} placeholder="Ex: (16) 99999-8888" size="large" />
                </Form.Item>
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 24 }}>
                    <Button onClick={onCancel} size="large">Cancelar</Button>
                    <Button type="primary" htmlType="submit" loading={loading} size="large">
                        {isEditing ? 'Salvar Alterações' : 'Cadastrar Fornecedor'}
                    </Button>
                </div>
            </Form>
        </Modal>
    );
};


// Componente "Pai": A Página de Fornecedores
const SupplierPage = () => {
    const [suppliers, setSuppliers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [editingSupplier, setEditingSupplier] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchSuppliers = useCallback(async () => {
        setLoading(true);
        try {
            // PASSO 1 (CORRIGIDO): Usando o método padrão '.get'
            const response = await ApiService.get('/suppliers/');
            setSuppliers(response.data);
        } catch (error) {
            message.error('Falha ao carregar fornecedores.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSuppliers();
    }, [fetchSuppliers]);

    // A FUNÇÃO CHAVE: Define o que fazer após o sucesso do formulário.
    const handleFormSuccess = () => {
        message.success(`Fornecedor ${editingSupplier ? 'atualizado' : 'cadastrado'} com sucesso!`);
        setIsModalVisible(false); // 1. Fecha o modal
        setEditingSupplier(null);
        fetchSuppliers();       // 2. Atualiza a lista
    };

    const handleCancel = () => { setIsModalVisible(false); setEditingSupplier(null); };
    const showCreateModal = () => { setEditingSupplier(null); setIsModalVisible(true); };
    const showEditModal = (supplier) => { setEditingSupplier(supplier); setIsModalVisible(true); };

    const handleDelete = async (supplierId) => {
        try {
            // PASSO 1 (CORRIGIDO): Usando o método padrão '.delete'
            await ApiService.delete(`/suppliers/${supplierId}`);
            message.success('Fornecedor excluído com sucesso!');
            fetchSuppliers();
        } catch (error) {
            message.error('Erro ao excluir o fornecedor.');
        }
    };

    const filteredSuppliers = useMemo(() => {
        if (!searchTerm) return suppliers;
        return suppliers.filter(s =>
            s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (s.contact_person && s.contact_person.toLowerCase().includes(searchTerm.toLowerCase()))
        );
    }, [suppliers, searchTerm]);

    const gridVariants = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.05 } } };
    const cardVariants = { hidden: { y: 20, opacity: 0 }, visible: { y: 0, opacity: 1 } };

    return (
        <>
            <PageStyles />
            <motion.div className="supplier-page-container" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <div className="supplier-header">
                    <Title level={2} style={{ color: 'white', margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
                        <TeamOutlined /> Gestão de Fornecedores
                    </Title>
                </div>
                
                <Card className="controls-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Search
                            placeholder="Buscar por nome ou contato..."
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{ maxWidth: 400 }}
                            allowClear
                            size="large"
                        />
                        <Button type="primary" icon={<PlusOutlined />} onClick={showCreateModal} size="large">
                            Adicionar Fornecedor
                        </Button>
                    </div>
                </Card>

                {loading ? <div style={{textAlign: 'center', padding: 50}}><Spin size="large" /></div> : (
                    <AnimatePresence>
                        {filteredSuppliers.length > 0 ? (
                            <motion.div className="supplier-grid" variants={gridVariants} initial="hidden" animate="visible">
                                {filteredSuppliers.map(supplier => (
                                    <motion.div key={supplier.id} variants={cardVariants}>
                                        <Card className="supplier-card">
                                            <div className="card-actions">
                                                <Space>
                                                    <Tooltip title="Editar"><Button shape="circle" icon={<EditOutlined />} onClick={() => showEditModal(supplier)} /></Tooltip>
                                                    <Popconfirm title="Tem certeza?" onConfirm={() => handleDelete(supplier.id)} okText="Sim" cancelText="Não">
                                                        <Tooltip title="Excluir"><Button shape="circle" danger icon={<DeleteOutlined />} /></Tooltip>
                                                    </Popconfirm>
                                                </Space>
                                            </div>
                                            <Space align="start">
                                                <Avatar size={48} icon={<TeamOutlined />} style={{backgroundColor: '#16a085'}}/>
                                                <div>
                                                    <Title level={4} style={{marginBottom: 0}}>{supplier.name}</Title>
                                                    <Text type="secondary">{supplier.contact_person || "Sem contato principal"}</Text>
                                                </div>
                                            </Space>
                                            <div className="contact-info">
                                                {supplier.email && <Text><MailOutlined style={{marginRight: 8, color: '#3498db'}}/> {supplier.email}</Text>}
                                                {supplier.phone_number && <Text><PhoneOutlined style={{marginRight: 8, color: '#3498db'}}/> {supplier.phone_number}</Text>}
                                            </div>
                                        </Card>
                                    </motion.div>
                                ))}
                            </motion.div>
                        ) : (
                            <Empty description={<Title level={5} style={{color: '#888'}}>Nenhum fornecedor encontrado.</Title>} />
                        )}
                    </AnimatePresence>
                )}

                <SupplierFormModal
                    visible={isModalVisible}
                    onCancel={handleCancel}
                    onSuccess={handleFormSuccess}
                    editingSupplier={editingSupplier}
                />
            </motion.div>
        </>
    );
};

export default SupplierPage;